from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from celery import shared_task

from common.utils import get_logger
from common.libs.prmk_client import SSHClient
from common.tasks import send_mail_async
from assets.models.asset import Asset
from .models import Database, Command
from ops.celery.utils import register_as_period_task, after_app_ready_start, after_app_shutdown_clean

logger = get_logger(__file__)


# @shared_task
# def execute_transfer_task(*args, **kwargs):
#     task_name = kwargs.get('task_name')
#     schedule = PeriodicTask.objects.get(name=task_name).transferschedule
#     database = Database.objects.get(id=kwargs.get('database'))
#     user_owner = database.user_owner
#     command_list = schedule.commands.all()
#     ip = database.label.assets.first().ip
#     result = execute_command(ip=ip, cmd_user=user_owner, command_list=command_list)
#     if result:
#         send_mail_async('[生产-NAS]任务下发通知', '您的[生产-NAS]任务 %s 已下发，请知晓~' % task_name, [schedule.creator.email])


@shared_task
@register_as_period_task(interval=60)
@after_app_ready_start
@after_app_shutdown_clean
def execute_command():
    assets = Asset.objects.filter(labels__value__in=['生产环境', '测试环境'])
    for asset in assets:
        ip = asset.ip
        system_user = asset.systemuser_set.first()
        username = system_user.username
        password = system_user.password
        ssh = SSHClient(hostname=ip, port=22, username=username, password=password)
        for i in range(3):
            ssh.connect()
            if ssh.client_state:
                break
        else:
            if not ssh.client_state:
                return False
        sch_num = cache.get('SCHEDULE_NUM_%s' % ip, 0)
        max_con = asset.max_con
        commands = Command.objects.filter(schedule__database__asset=asset, status=0,
                                          schedule__run_time__lte=timezone.now())[:max_con-sch_num]
        ssh.get_shell()
        shell = ssh.shell
        if not shell:
            ssh.close()
            return False

        for command in commands:
            cmd_user = command.schedule.database.user_owner
            shell.send('sudo su - %s\n' % cmd_user)
            cmd = command.content + ' %s\n' % str(command.id)
            # to do 确定返回值，判断执行结果
            shell.send(cmd)
            # shell.send('exit\n')
            command.status = 1
            command.save(update_fields=['status'])
            sch_num += 1
        ssh.close()
        cache.set('SCHEDULE_NUM_%s' % ip, sch_num, 60 * 60 * 24 * 5)


@shared_task
@register_as_period_task(interval=60)
@after_app_ready_start
@after_app_shutdown_clean
def check_schedule_result():
    assets = Asset.objects.filter(labels__value__in=['生产环境', '测试环境'])
    for asset in assets:
        ip = asset.ip
        system_user = asset.systemuser_set.first()
        username = system_user.username
        password = system_user.password
        log_dir = asset.log_dir
        ssh = SSHClient(hostname=ip, port=22, username=username, password=password)
        for i in range(3):
            ssh.connect()
            if ssh.client_state:
                break
        else:
            if not ssh.client_state:
                return False
        commands = Command.objects.filter(schedule__database__asset=asset, status=1)
        sch_num = cache.get('SCHEDULE_NUM_%s' % ip, 0)
        for command in commands:
            cmd = 'cat %s/%s' % (log_dir+timezone.now().strftime('%Y%m%d'), str(command.id))
            stdout, stderr = ssh.run_cmd(cmd)
            if stderr:
                send_mail_async.delay(
                    'Check schedule result error',
                    'asset: %s\n' % ip + 'command: %s\n' % cmd + 'err: %s' % stderr,
                    [item[-1] for item in settings.ADMINS]
                )
                command.status = 3
                command.save(update_fields=['status'])
                sch_num -= 1
                continue
            status = get_status(log_info=stdout, content=command.content)
            if status:
                command.status = status
                command.save(update_fields=['status'])

                sch_num -= 1
        cache.set('SCHEDULE_NUM_%s' % ip, sch_num, 60*60*24*5)


def get_status(log_info, content):
    return 2


@shared_task
def schedule_inform_email():
    pass
