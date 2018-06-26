import uuid

from django.db import models


class Database(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100, verbose_name='库名', unique=True)
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

    class Meta:
        ordering = ('name', )
        verbose_name = '库'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Table(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
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
