# -*- coding: utf-8 -*-
#

from rest_framework import serializers
from rest_framework_bulk.serializers import BulkListSerializer

from common.mixins import BulkSerializerMixin
from .models import Database, Table, Field


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

    class Meta:
        model = Database
        list_serializer_class = BulkListSerializer
        fields = '__all__'


