import json
import random
import string
from functools import wraps

from django.db.utils import ProgrammingError, OperationalError
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

from .models import TransferSchedule, Database, Table, Command


def create_or_update_schedule_task(task):
    """
    :param task: {
        'name': '定时任务001',
        'task': 'tasks.add', # A registered celery task,
        'crontab': "30 7 * * *",
        'args': (16, 16),
        'kwargs': {},
        'enabled': False,
        'schedule': {
            'type': 0,
            'comment': '',
            'user': User,
        }
    }
    :return:
    """
    # Todo: check task valid, task and callback must be a celery task
    try:
        IntervalSchedule.objects.all().count()
    except (ProgrammingError, OperationalError):
        return None

    if isinstance(task.get("crontab"), str):
        try:
            minute, hour, day, month, week = task["crontab"].split()
        except ValueError:
            raise SyntaxError("crontab is not valid")
        kwargs = dict(
            minute=minute, hour=hour, day_of_week=week,
            day_of_month=day, month_of_year=month,
        )
        crontab = CrontabSchedule.objects.create(**kwargs)
    else:
        raise SyntaxError("TransferSchedule is not valid")

    task_defaults = dict(
        crontab=crontab,
        name=task['name'],
        task=task['task'],
        args=json.dumps(task.get('args', [])),
        kwargs=json.dumps(task.get('kwargs', {})),
        enabled=task.get('enabled', True),
    )
    periodic_task = PeriodicTask.objects.update_or_create(
        defaults=task_defaults, name=task['name'],
    )
    schedule_defaults = dict(
        periodic=periodic_task,
        type=task['schedule'].get('type', 0),
        comment=task['schedule'].get('comment', '')
    )
    try:
        schedule = TransferSchedule.objects.get(periodic=periodic_task)
    except TransferSchedule.DoesNotExist:
        schedule_defaults.update(creator=task['schedule'].get('user'))
        schedule = TransferSchedule.objects.create(**schedule_defaults)
    else:
        schedule.type = schedule_defaults['type']
        schedule.comment = schedule_defaults['comment']
        schedule.modifier = task['schedule'].get('user')
        schedule.save()

    return schedule


def create_task_name(database_id):
    try:
        database = Database.objects.get(id=database_id)
    except Database.DoesNotExist:
        return
    database_name = database.__str__()
    task_name = database_name + timezone.localtime(timezone.now()).strftime('-%Y-%m-%d_%H-%M-%S')
    if not PeriodicTask.objects.filter(name=task_name):
        return task_name
    for i in range(10):
        random_str = '_' + ''.join(random.sample(string.ascii_letters + string.digits, 3))
        task_name += random_str
        if not PeriodicTask.objects.filter(name=task_name):
            return task_name


def create_import_cmd(database_id, tables_id_list):
    try:
        database = Database.objects.get(id=database_id)
    except Database.DoesNotExist:
        return []
    cmd = []
    database_name = database.name
    for table_id in tables_id_list:
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            break
        table_name = table.name
        cmd.append(
            '/appdata/hadoopbak/shell/bachBackupHdfs.sh /user/hive/warehouse/{db}/{table}'.format(
                db=database_name, table=table_name)
        )
    return cmd


def create_export_cmd(database_id, tables_id_list):
    try:
        database = Database.objects.get(id=database_id)
    except Database.DoesNotExist:
        return []
    cmd = []
    database_name = database.name
    for table_id in tables_id_list:
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            break
        table_name = table.name
        cmd.append(
            '/appdata/hadoopbak/shell/bachBackup.sh /appdata/hadoopbak/user/hive/warehouse/{db}/{table}'.format(
                db=database_name, table=table_name)
        )
    return cmd

