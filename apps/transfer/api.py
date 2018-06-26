from rest_framework import viewsets
from rest_framework_bulk import BulkModelViewSet, ListBulkCreateUpdateAPIView
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404

from common.mixins import IDInFilterMixin
from common.permissions import IsSuperUserOrAppUser, IsValidUser
from .models import Database, Table, Field
from .serializers import DatabaseSerializer, TableSerializer, FieldSerializer


class DatabaseViewSet(IDInFilterMixin, BulkModelViewSet):
    filter_fields = ("name", "dev", 'opr', 'comment')
    search_fields = filter_fields
    ordering_fields = ("name", )
    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class TableViewSet(IDInFilterMixin, BulkModelViewSet):
    filter_fields = ("database", "name", "dev", 'opr', 'comment')
    search_fields = filter_fields
    ordering_fields = ("name", )
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class FieldViewSet(IDInFilterMixin, BulkModelViewSet):
    filter_fields = ("table", "name")
    search_fields = filter_fields
    ordering_fields = ("name", )
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset
