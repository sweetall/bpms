# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals
from rest_framework import serializers
from django_celery_beat.models import PeriodicTask

from .models import Task, AdHoc, AdHocRunHistory, Schedule


# add start
class PeriodicTaskSerializer(serializers.ModelSerializer):
    crontab_info = serializers.SerializerMethodField()

    def get_crontab_info(self, obj):
        return obj.crontab.__str__()

    class Meta:
        model = PeriodicTask
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    periodic = PeriodicTaskSerializer(read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'

# add end


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class AdHocSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdHoc
        exclude = ('_tasks', '_options', '_hosts', '_become')

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        fields.extend(['tasks', 'options', 'hosts', 'become', 'short_id'])
        return fields


class AdHocRunHistorySerializer(serializers.ModelSerializer):
    task = serializers.SerializerMethodField()
    adhoc_short_id = serializers.SerializerMethodField()
    stat = serializers.SerializerMethodField()

    class Meta:
        model = AdHocRunHistory
        exclude = ('_result', '_summary')

    @staticmethod
    def get_adhoc_short_id(obj):
        return obj.adhoc.short_id

    @staticmethod
    def get_task(obj):
        return obj.adhoc.task.id

    @staticmethod
    def get_stat(obj):
        return {
            "total": len(obj.adhoc.hosts),
            "success": len(obj.summary.get("contacted", [])),
            "failed": len(obj.summary.get("dark", [])),
        }

    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)
        fields.extend(['summary', 'short_id'])
        return fields
