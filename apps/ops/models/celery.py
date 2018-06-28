# -*- coding: utf-8 -*-
#
import uuid
import os
import json
import datetime
from django.conf import settings
from django.db import models
from django_celery_beat.models import PeriodicTask

from common.mixins import UserMixin, DateMixin


# add start
class Schedule(UserMixin, DateMixin):
    TYPE_CHOICES = (
        (1, '数据导出'),
        (2, '数据导入'),
    )
    STATUS_CHOICES = (
        (1, '等待执行'),
        (2, '取消执行'),
        (3, '执行中..'),
        (4, '执行成功'),
        (5, '执行失败'),
        (6, '过期未执行'),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    periodic = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE, verbose_name='任务')
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name='类型')
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name='状态')
    comment = models.TextField(max_length=200, verbose_name='备注')

    @property
    def crontab_info(self):
        crontab = self.periodic.crontab
        k = json.loads(self.periodic.kwargs).get('year', '')
        return k + '-' + crontab.month_of_year + '-' + crontab.day_of_month + ' ' + crontab.hour + ':' + crontab.minute

    @property
    def type_info(self):
        return self.TYPE_CHOICES[self.type - 1][-1]

    @property
    def kwargs_dict(self):
        return json.loads(self.periodic.kwargs)

    @property
    def status_info(self):
        crontab_time = datetime.datetime.strptime(self.crontab_info, '%Y-%m-%d %H:%M')
        now_time = datetime.datetime.now()
        if crontab_time < now_time and self.status in [1, 2, 6]:
            self.periodic.enabled = False
            self.periodic.save(update_fields=['enabled'])
            self.status = 6
            self.save(update_fields=['status'])
            return self.STATUS_CHOICES[self.status-1][-1]
        if crontab_time > now_time and not self.periodic.enabled and self.status != 2:
            self.status = 2
            self.save()
            return self.STATUS_CHOICES[self.status - 1][-1]
        if crontab_time > now_time and self.periodic.enabled and self.status != 1:
            self.status = 1
            self.save()
            return self.STATUS_CHOICES[self.status - 1][-1]
        return self.STATUS_CHOICES[self.status-1][-1]

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
