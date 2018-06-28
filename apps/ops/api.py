# ~*~ coding: utf-8 ~*~
import uuid
import os

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.http.response import JsonResponse
from rest_framework import viewsets, generics, mixins
from rest_framework.views import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import api_view, permission_classes
from django_celery_beat.models import PeriodicTask

from common.permissions import IsValidUser
from .hands import IsSuperUser
from .models import Task, AdHoc, AdHocRunHistory, CeleryTask, Schedule
from .serializers import TaskSerializer, AdHocSerializer, \
    AdHocRunHistorySerializer, ScheduleSerializer
from .tasks import run_ansible_task


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsSuperUser,)


class TaskRun(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskViewSet
    permission_classes = (IsSuperUser,)

    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        t = run_ansible_task.delay(str(task.id))
        return Response({"task": t.id})


class AdHocViewSet(viewsets.ModelViewSet):
    queryset = AdHoc.objects.all()
    serializer_class = AdHocSerializer
    permission_classes = (IsSuperUser,)

    def get_queryset(self):
        task_id = self.request.query_params.get('task')
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            self.queryset = self.queryset.filter(task=task)
        return self.queryset


class AdHocRunHistorySet(viewsets.ModelViewSet):
    queryset = AdHocRunHistory.objects.all()
    serializer_class = AdHocRunHistorySerializer
    permission_classes = (IsSuperUser,)

    def get_queryset(self):
        task_id = self.request.query_params.get('task')
        adhoc_id = self.request.query_params.get('adhoc')
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            adhocs = task.adhoc.all()
            self.queryset = self.queryset.filter(adhoc__in=adhocs)

        if adhoc_id:
            adhoc = get_object_or_404(AdHoc, id=adhoc_id)
            self.queryset = self.queryset.filter(adhoc=adhoc)
        return self.queryset


class CeleryTaskLogApi(generics.RetrieveAPIView):
    permission_classes = (IsSuperUser,)
    buff_size = 1024 * 10
    end = False
    queryset = CeleryTask.objects.all()

    def get(self, request, *args, **kwargs):
        mark = request.query_params.get("mark") or str(uuid.uuid4())
        task = self.get_object()
        log_path = task.full_log_path

        if not log_path or not os.path.isfile(log_path):
            return Response({"data": _("Waiting ...")}, status=203)

        with open(log_path, 'r') as f:
            offset = cache.get(mark, 0)
            f.seek(offset)
            data = f.read(self.buff_size).replace('\n', '\r\n')
            mark = str(uuid.uuid4())
            cache.set(mark, f.tell(), 5)

            if data == '' and task.is_finished():
                self.end = True
            return Response({"data": data, 'end': self.end, 'mark': mark})


class ScheduleViewSet(viewsets.ModelViewSet):  # mixins.ListModelMixin, generics.GenericAPIView
    filter_fields = ("periodic", "type")
    search_fields = filter_fields
    ordering_fields = ("create_time", )
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)
    http_method_names = ('get', )

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(creator=self.request.user)


@api_view(['POST'])
@permission_classes((IsValidUser, ))
def active_task(request):
    task_name = request.data.get('task_name')
    try:
        task = PeriodicTask.objects.get(name=task_name)
    except PeriodicTask.DoesNotExist:
        return Response({'status': False, 'message': '任务不存在！'})
    if task.schedule.creator != request.user:
        return Response({'status': False, 'message': '不可操作非自己的任务！'})
    task.enabled = not task.enabled
    task.save()
    return Response({'status': True, 'message': '状态修改成功！'})


@api_view(['POST'])
@permission_classes((IsValidUser, ))
def delete_task(request):
    task_name = request.data.get('task_name')
    try:
        task = PeriodicTask.objects.get(name=task_name)
    except PeriodicTask.DoesNotExist:
        return Response({'status': False, 'message': '任务不存在！'})
    if task.schedule.creator != request.user:
        return Response({'status': False, 'message': '不可删除非自己的任务！'})
    task.crontab.delete()
    return Response({'status': True, 'message': '删除成功！'})