# -*- coding: utf-8 -*-
#

from rest_framework import serializers
from rest_framework_bulk.serializers import BulkListSerializer
from django_celery_beat.models import PeriodicTask

from common.mixins import BulkSerializerMixin
from .models import Database, Table, Field, Schedule, Command


class FieldSerializer(BulkSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Field
        list_serializer_class = BulkListSerializer
        fields = '__all__'


class TableSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        list_serializer_class = BulkListSerializer
        fields = '__all__'


class DatabaseSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    tables = TableSerializer(many=True, read_only=True)
    label_info = serializers.SerializerMethodField()

    def get_label_info(self, obj):
        return obj.label_info

    class Meta:
        model = Database
        list_serializer_class = BulkListSerializer
        fields = '__all__'


class PeriodicTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = PeriodicTask
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    periodic = PeriodicTaskSerializer(read_only=True)
    crontab_info = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    type_info = serializers.SerializerMethodField()
    status_info = serializers.SerializerMethodField()
    kwargs_dict = serializers.SerializerMethodField()

    def get_crontab_info(self, obj):
        return obj.crontab_info

    def get_creator(self, obj):
        return obj.creator.username

    def get_type_info(self, obj):
        return obj.type_info

    def get_status_info(self, obj):
        return obj.status_info

    def get_kwargs_dict(self, obj):
        return obj.kwargs_dict

    class Meta:
        model = Schedule
        fields = '__all__'


class CommandSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)
    table = TableSerializer(read_only=True)
    status_info = serializers.SerializerMethodField()

    def get_status_info(self, obj):
        return obj.status_info

    class Meta:
        model = Command
        fields = '__all__'
