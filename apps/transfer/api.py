import datetime

from django.utils import timezone
from rest_framework import viewsets
from rest_framework_bulk import BulkModelViewSet, ListBulkCreateUpdateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import Response
from django.shortcuts import get_object_or_404

from common.mixins import IDInFilterMixin
from common.permissions import IsSuperUserOrAppUser, IsValidUser
from .models import Database, Table, Field, TransferSchedule, Command
from .serializers import DatabaseSerializer, TableSerializer, FieldSerializer, ScheduleSerializer, CommandSerializer


class DatabaseViewSet(IDInFilterMixin, BulkModelViewSet):
    filter_fields = ("name", "dev", 'opr', 'bus', 'comment')
    search_fields = filter_fields
    ordering_fields = ("name", )
    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class TableViewSet(IDInFilterMixin, BulkModelViewSet):
    filter_fields = ("database", "name", "dev", 'opr', 'bus', 'comment')
    search_fields = filter_fields
    ordering_fields = ("name", )
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class FieldViewSet(IDInFilterMixin, BulkModelViewSet):
    filter_fields = ("table", "name")
    search_fields = filter_fields
    ordering_fields = ("name", )
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class ScheduleViewSet(viewsets.ModelViewSet):  # mixins.ListModelMixin, generics.GenericAPIView
    filter_fields = ("database", "type")
    search_fields = filter_fields
    ordering_fields = ("create_time", )
    queryset = TransferSchedule.objects.all()
    serializer_class = ScheduleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)
    http_method_names = ('get', )

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(creator=self.request.user)


class CommandViewSet(viewsets.ModelViewSet):
    filter_fields = ('schedule', 'table', 'status')
    ordering_fields = ("id",)
    search_fields = filter_fields
    queryset = Command.objects.all()
    serializer_class = CommandSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)
    http_method_names = ('get', )

    def get_queryset(self):
        return super().get_queryset()


class UserCommandViewSet(CommandViewSet):

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(schedule__creator=self.request.user)


# add
@api_view(['POST'])
@permission_classes((IsValidUser, ))
def active_transfer_task(request):
    task_id = request.data.get('task_id')
    try:
        task = TransferSchedule.objects.get(id=task_id)
    except TransferSchedule.DoesNotExist:
        return Response({'status': False, 'message': '任务不存在！'})
    if task.creator != request.user:
        return Response({'status': False, 'message': '不可操作非自己的任务！'})

    run_time = task.run_time
    now_time = timezone.now()
    if run_time < now_time:
        return Response({'status': False, 'message': '不可操作已过期的任务！'})

    task.status = 0 if task.status else 1
    task.save(update_fields=['status'])
    return Response({'status': True, 'message': '状态修改成功！'})


@api_view(['POST'])
@permission_classes((IsValidUser, ))
def delete_transfer_task(request):
    task_id = request.data.get('task_id')
    try:
        task = TransferSchedule.objects.get(id=task_id)
    except TransferSchedule.DoesNotExist:
        return Response({'status': False, 'message': '任务不存在！'})
    # can not del other's task
    if task.creator != request.user:
        return Response({'status': False, 'message': '不可删除非自己的任务！'})
    # can not del the task has been executed
    run_time = task.run_time
    now_time = timezone.now()
    if run_time < now_time and task.status > 1:
        return Response({'status': False, 'message': '不可删除此任务！'})
    # if safe, del it
    task.delete()
    return Response({'status': True, 'message': '删除成功！'})
