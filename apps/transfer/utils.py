import json
import random
import string
from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.db.utils import ProgrammingError, OperationalError
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.shortcuts import reverse, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .models import TransferSchedule, Database, Table, Command


def create_or_update_schedule_task(task):
    try:
        schedule = task.get('schedule')
        schedule_defaults = task['schedule_defaults']
        command_list = task['command_list']
        if schedule:
            schedule.database = schedule_defaults['database']
            schedule.name = schedule_defaults['name']
            schedule.run_time = schedule_defaults['run_time']
            schedule.type = schedule_defaults['type']
            schedule.comment = schedule_defaults['comment']
            schedule.modifier = task['user']
            if task.get('from_schedule'):
                schedule.from_schedule = task['from_schedule']
            schedule.save(update_fields=['name', 'run_time', 'type', 'comment'])

            schedule.commands.all().delete()
        else:
            schedule_defaults.update({'creator': task['user']})
            schedule = TransferSchedule.objects.create(**schedule_defaults)

        for command in command_list:
            command_defaults = {
                'schedule': schedule,
                'table': Table.objects.get(id=command[0]),
                'content': command[1]
            }
            Command.objects.create(**command_defaults)
    except Exception as err:
        return str(err)


def create_task_name(database):
    database_name = database.__str__()
    task_name = database_name + timezone.localtime(timezone.now()).strftime('-%Y-%m-%d_%H-%M-%S')
    if not PeriodicTask.objects.filter(name=task_name):
        return task_name
    for i in range(10):
        random_str = '_' + ''.join(random.sample(string.ascii_letters + string.digits, 3))
        task_name += random_str
        if not PeriodicTask.objects.filter(name=task_name):
            return task_name


def create_transfer_cmd(database, tables_id_list):
    cmd_format = database.asset.cmd_format
    cmd = []
    database_name = database.name
    for table_id in tables_id_list:
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            break
        table_name = table.name
        cmd.append((table_id, cmd_format.format(db=database_name, table=table_name)))
    return cmd


# check the schedule has ran or not, if has ran more than 1 times, can't edit it
class ScheduleEditableAccessMixin(AccessMixin):
    def editable(self):
        pk = self.request.META.get("PATH_INFO").split('/')[-3]
        schedule = get_object_or_404(TransferSchedule, id=pk)
        if schedule.run_time < timezone.now() and schedule.status in [2, 3, 4]:
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        schedule_type = self.request.META.get("PATH_INFO").split('/')[-4]
        if not self.editable():
            messages.error(request, '当前任务不可编辑！')
            return HttpResponseRedirect(reverse_lazy('transfer:%s-list' % schedule_type))
        return super().dispatch(request, *args, **kwargs)
