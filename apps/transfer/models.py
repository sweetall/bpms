import uuid
import json
import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask

from common.mixins import UserMixin, DateMixin
from assets.models.label import Label


# # 待补充，与源库字段保持一致
# class Subsystem(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, primary_key=True)
#     name = models.CharField(max_length=200, verbose_name='英文简称')
#     dev = models.CharField(blank=True, max_length=100, verbose_name='对应开发')
#     opr = models.CharField(blank=True, max_length=100, verbose_name='对应运维')
#     comment = models.TextField(max_length=200, default='', blank=True, verbose_name='备注')
#     modifier = models.CharField(default='Admin', blank=True, max_length=50, verbose_name='最近修改人')
#     modify_time = models.DateTimeField(blank=True, editable=False, auto_now=True)
#
#     class Meta:
#         ordering = ('name',)
#         verbose_name = '子系统'
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.name


class Database(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    label = models.ForeignKey(Label, blank=True, null=True, related_name='databases', on_delete=models.SET_NULL,
                              verbose_name='标签')
    name = models.CharField(max_length=100, verbose_name='库名')
    quota = models.IntegerField(verbose_name='配额')
    # used = models.IntegerField(verbose_name='使用量')
    # daily_increase = models.IntegerField(blank=True, verbose_name='日增量')

    is_active = models.BooleanField(default=True, verbose_name='是否可用')
    dev = models.CharField(blank=True, max_length=100, verbose_name='对应开发')
    opr = models.CharField(blank=True, max_length=100, verbose_name='对应运维')
    bus = models.CharField(blank=True, max_length=100, verbose_name='对应业务')
    comment = models.TextField(max_length=200, default='', blank=True, verbose_name='备注')
    modifier = models.CharField(default='Admin', blank=True, max_length=50, verbose_name='最近修改人')
    modify_time = models.DateTimeField(blank=True, editable=False, auto_now=True)

    @property
    def label_info(self):
        return self.label.__str__() if self.label else ''

    class Meta:
        ordering = ('name', )
        verbose_name = '库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Table(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    # subsystem = models.ForeignKey(Subsystem, blank=True, related_name='tables', on_delete=models.SET_NULL,
    #                               verbose_name='子系统')
    database = models.ForeignKey(Database, related_name='tables', on_delete=models.CASCADE, verbose_name='对应库')
    name = models.CharField(max_length=100, verbose_name='表名')
    format = models.CharField(max_length=100, verbose_name='存储格式')
    table_create_time = models.CharField(max_length=100, verbose_name='创建时间')
    table_update_time = models.CharField(max_length=100, verbose_name='更新时间')
    is_partitioned = models.BooleanField(default=False, verbose_name='是否分区')
    partition_field = models.CharField(max_length=100, blank=True, verbose_name='分区字段')
    # size = models.IntegerField(blank=True, verbose_name='大小(byte)')
    # daily_increase = models.IntegerField(blank=True, verbose_name='日增量')

    is_active = models.BooleanField(default=True, verbose_name='是否可用')
    dev = models.CharField(blank=True, max_length=100, verbose_name='对应开发')
    opr = models.CharField(blank=True, max_length=100, verbose_name='对应运维')
    bus = models.CharField(blank=True, max_length=100, verbose_name='对应业务')
    comment = models.TextField(max_length=200, default='', blank=True, verbose_name='备注')
    modifier = models.CharField(default='Admin', blank=True, max_length=50, verbose_name='最近修改人')
    modify_time = models.DateTimeField(blank=True, editable=False, auto_now=True)

    class Meta:
        ordering = ('name', )
        verbose_name = '表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.database.name + '-' + self.name


class Field(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    table = models.ForeignKey(Table, related_name='fields', on_delete=models.CASCADE, verbose_name='对应表')
    name = models.CharField(max_length=100, verbose_name='字段名')
    type = models.CharField(max_length=100, verbose_name='类型')

    is_sensitive = models.BooleanField(default=False, verbose_name='是否敏感')
    comment = models.TextField(max_length=200, default='', blank=True, verbose_name='备注')
    modifier = models.CharField(default='Admin', blank=True, max_length=50, verbose_name='最近修改人')
    modify_time = models.DateTimeField(blank=True, editable=False, auto_now=True)

    class Meta:
        ordering = ('name', )
        verbose_name = '字段'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.table.__str__() + '-' + self.name


class Schedule(UserMixin, DateMixin):
    TYPE_CHOICES = (
        (0, '数据导出'),
        (1, '数据导入'),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    periodic = models.OneToOneField(PeriodicTask, on_delete=models.CASCADE, verbose_name='任务')
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name='类型')
    comment = models.TextField(max_length=200, verbose_name='备注')

    @property
    def crontab_info(self):
        crontab = self.periodic.crontab
        k = json.loads(self.periodic.kwargs).get('year', '')
        return k + '-' + crontab.month_of_year + '-' + crontab.day_of_month + ' ' + crontab.hour + ':' + crontab.minute

    @property
    def type_info(self):
        return self.TYPE_CHOICES[self.type][-1]

    @property
    def kwargs_dict(self):
        return json.loads(self.periodic.kwargs)

    @property
    def status_info(self):
        crontab_time = datetime.datetime.strptime(self.crontab_info, '%Y-%m-%d %H:%M')
        now_time = datetime.datetime.now()
        if crontab_time > now_time:
            if self.periodic.enabled:
                return '等待执行'
            return '取消执行'
        if self.commands.filter(status=0):
            return '过期未执行'
        return '已执行'

    class Meta:
        ordering = ('create_time',)
        verbose_name = '定时任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.periodic.name


class Command(models.Model):
    STATUS_CHOICES = (
        (0, '未执行'),
        (1, '执行中..'),
        (2, '执行成功'),
        (3, '执行失败')
    )
    schedule = models.ForeignKey(Schedule, related_name='commands', on_delete=models.CASCADE, verbose_name='任务')
    table = models.ForeignKey(Table, related_name='commands', on_delete=models.CASCADE, verbose_name='表')
    content = models.CharField(max_length=1000, verbose_name='内容')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='状态')

    @property
    def status_info(self):
        return self.STATUS_CHOICES[self.status][-1]

    class Meta:
        ordering = ('schedule',)
        verbose_name = '命令'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


@receiver(post_save, sender=Schedule)
def create_or_update_command(sender, instance, created, **kwargs):
    task_kwargs = instance.kwargs_dict
    tables = task_kwargs.get('tables', [])
    cmd = task_kwargs.get('cmd', [])
    commands = instance.commands
    if not commands:
        for i, table_id in enumerate(tables):
            content = cmd[i]
            Command.objects.create(
                schedule=instance,
                table_id=table_id,
                content=content
            )
    else:
        commands.exclude(table_id__in=tables).delete()
        exist_tables_list = [str(x['table_id']) for x in commands.values('table_id', )]
        tables_list = list(filter(lambda x: x not in exist_tables_list, tables))
        for table_id in tables_list:
            content = cmd[tables.index(table_id)]
            Command.objects.create(
                schedule=instance,
                table_id=table_id,
                content=content
            )
