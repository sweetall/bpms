from django.conf import settings
from celery import shared_task
from common.utils import get_logger

logger = get_logger(__file__)


@shared_task
def import_task(*args, **kwargs):
    pass
