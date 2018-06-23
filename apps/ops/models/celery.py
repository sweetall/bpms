# -*- coding: utf-8 -*-
#
import uuid
import os
from django.conf import settings
from django.db import models
from django_celery_beat.models import PeriodicTask

from common.mixins import UserMixin, DateMixin


# add start
class Schedule(UserMixin, DateMixin):
    STYLE_CHOICES = (
        (1, '数据导出'),
        (2, '数据导入'),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    periodic = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE, verbose_name='任务')
    style = models.IntegerField(choices=STYLE_CHOICES, verbose_name='类型')
    comment = models.TextField(max_length=200, verbose_name='备注')

    class Meta:
        ordering = ('create_time',)
        verbose_name = '定时任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.periodic.name

# add end


class CeleryTask(models.Model):
    WAITING = "waiting"
    RUNNING = "running"
    FINISHED = "finished"
    LOG_DIR = os.path.join(settings.PROJECT_DIR, 'data', 'celery')

    STATUS_CHOICES = (
        (WAITING, WAITING),
        (RUNNING, RUNNING),
        (FINISHED, FINISHED),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=1024)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    log_path = models.CharField(max_length=256, blank=True, null=True)
    date_published = models.DateTimeField(auto_now_add=True)
    date_start = models.DateTimeField(null=True)
    date_finished = models.DateTimeField(null=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.id)

    def is_finished(self):
        return self.status == self.FINISHED

    @property
    def full_log_path(self):
        if not self.log_path:
            return None
        return os.path.join(self.LOG_DIR, self.log_path)
