from django.conf import settings
from celery import shared_task
from django_celery_beat.models import PeriodicTask

from common.utils import get_logger
from common.libs.prmk_client import SSHClient
from transfer.models import TransferSchedule, Command
from assets.models.asset import Asset
from assets.models.user import SystemUser

logger = get_logger(__file__)


@shared_task
def transfer_import_task(*args, **kwargs):
    task_name = kwargs.get('task_name')
    schedule = PeriodicTask.objects.get(name=task_name).schedule
    command_list = schedule.commands
    for command in command_list:
        cmd = command.content
        execute_command.delay(ip='', cmd=cmd)
        command.status = 1
        command.save()


@shared_task
def execute_command(ip, cmd):
    asset = Asset.objects.get(ip=ip)
    system_user = asset.systemuser_set[0]
    username = system_user.username
    password = system_user.password
    ssh = SSHClient(hostname=ip, port=22, username=username, password=password)
    ssh.connect()
    ssh.run_cmd(cmd=cmd)
    ssh.close()


# 1 下发命令 写入标记
# 2 检查进程 确定执行状态 pa -aux | grep cmd
# 3 进程消失 + 日志 判断执行结果 删除标记
