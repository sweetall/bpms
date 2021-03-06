# -*- coding: utf-8 -*-
#

from rest_framework import serializers
from rest_framework_bulk.serializers import BulkListSerializer
from django_celery_beat.models import PeriodicTask

from common.mixins import BulkSerializerMixin
from .models import Database, Table, Field, TransferSchedule, Command


class FieldSerializer(BulkSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Field
        list_serializer_class = BulkListSerializer
        fields = '__all__'


class TableSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)
    subsystem = serializers.SerializerMethodField()
    is_partitioned = serializers.SerializerMethodField()

    def get_subsystem(self, obj):
        if obj.subsystem:
            return obj.subsystem.en_name_abbr
        return ''

    def get_is_partitioned(self, obj):
        return '是' if obj.is_partitioned else '否'

    class Meta:
        model = Table
        list_serializer_class = BulkListSerializer
        fields = '__all__'


class DatabaseSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    tables = TableSerializer(many=True, read_only=True)
    asset_info = serializers.SerializerMethodField()
    asset = serializers.SerializerMethodField()

    def get_asset_info(self, obj):
        return obj.asset_info

    def get_asset(self, obj):
        if obj.asset:
            return obj.asset.ip
        return ''

    class Meta:
        model = Database
        list_serializer_class = BulkListSerializer
        fields = '__all__'


# class PeriodicTaskSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = PeriodicTask
#         fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()
    type_info = serializers.SerializerMethodField()
    status_info = serializers.SerializerMethodField()
    command_list = serializers.SerializerMethodField()

    def get_creator(self, obj):
        return obj.creator.username

    def get_type_info(self, obj):
        return obj.type_info

    def get_status_info(self, obj):
        return obj.status_info

    def get_command_list(self, obj):
        return obj.command_list

    class Meta:
        model = TransferSchedule
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
