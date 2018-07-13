from django.conf import settings
from celery import shared_task
from django_celery_beat.models import PeriodicTask

from common.utils import get_logger
from common.libs.prmk_client import SSHClient
from common.tasks import send_mail_async
from assets.models.asset import Asset
from .models import Database

logger = get_logger(__file__)


@shared_task
def execute_transfer_task(*args, **kwargs):
    task_name = kwargs.get('task_name')
    schedule = PeriodicTask.objects.get(name=task_name).transferschedule
    command_list = schedule.commands.all()
    ip = Database.objects.get(id=kwargs.get('database')).label.assets.first().ip
    result = execute_command(ip=ip, command_list=command_list)
    if result:
        send_mail_async('[生产-NAS]任务下发通知', '您的[生产-NAS]任务 %s 已下发，请知晓~' % task_name, [schedule.creator.email])


# @shared_task
def execute_command(ip, command_list):
    asset = Asset.objects.get(ip=ip)
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
    for command in command_list:
        cmd = command.content
        # to do 确定返回值，判断执行结果
        result = ssh.run_cmd(cmd=cmd)
        print('*'*40)
        command.status = 1
        command.machine = ip
        command.save()
    ssh.close()
    return True


# 1 下发命令 写入标记
# 2 检查进程 确定执行状态 pa -aux | grep cmd
# 3 进程消失 + 日志 判断执行结果 删除标记
