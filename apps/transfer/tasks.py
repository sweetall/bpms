from django.conf import settings
from celery import shared_task

from common.utils import get_logger
from common.libs.prmk_client import SSHClient

logger = get_logger(__file__)


@shared_task
def transfer_task(*args, **kwargs):
    task_name = kwargs.get('task_name')
    cmd_list = kwargs.get('cmd', [])
    database_id = kwargs.get('database')

    pass


@shared_task
def execute_import(database_id, cmd_list):

    pass
