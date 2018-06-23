from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .utils import get_logger

from .libs.prmk_client import SSHClient
# from assets.models.asset import Asset
# from assets.models.user import SystemUser
# from assets.serializers.system_user import SystemUserAuthSerializer

logger = get_logger(__file__)


@shared_task
def send_mail_async(*args, **kwargs):
    """ Using celery to send email async

    You can use it as django send_mail function

    Example:
    send_mail_sync.delay(subject, message, from_mail, recipient_list, fail_silently=False, html_message=None)

    Also you can ignore the from_mail, unlike django send_mail, from_email is not a require args:

    Example:
    send_mail_sync.delay(subject, message, recipient_list, fail_silently=False, html_message=None)
    """
    if len(args) == 3:
        args = list(args)
        args[0] = settings.EMAIL_SUBJECT_PREFIX + args[0]
        args.insert(2, settings.EMAIL_HOST_USER)
        args = tuple(args)

    try:
        send_mail(*args, **kwargs)
    except Exception as e:
        logger.error("Sending mail error: {}".format(e))


@shared_task
def send_mail_test():
    send_status = send_mail(subject='【BPMS】Celery测试邮件', message='Celery与Beat运行正常～',
                            from_email='sweet_all@sina.com', recipient_list=(settings.ADMINS[0][1], ))
    return send_status


# @shared_task
# def execute_cmd(**kwargs):
#     asset_id = kwargs.get('asset_id')
#     sys_user_id = kwargs.get('sys_user_id')
#     cmd = kwargs.get('cmd')
#     try:
#         asset = Asset.objects.get(id=asset_id)
#     except Asset.DoesNotExist:
#         return False
#     try:
#         sys_user = SystemUser.objects.get(id=sys_user_id)
#         sys_user = SystemUserAuthSerializer(instance=sys_user).data
#     except SystemUser.DoesNotExist:
#         return False
#     ssh = SSHClient(hostname=asset.hostname, username=sys_user.username, password=sys_user.password, port=22)
#     ssh.connect()
#     if ssh.client_state:
#         ssh.run_cmd(cmd)
#     else:
#         return False
#
#
@shared_task
def demo_start_nginx():
    ssh = SSHClient(hostname='172.18.0.12', username='root', password='092397', port=22)
    ssh.connect()
    if ssh.client_state:
        ssh.run_cmd('/usr/local/nginx/sbin/nginx')
        return True
    else:
        return False

