from rest_framework import viewsets
from rest_framework_bulk import BulkModelViewSet, ListBulkCreateUpdateAPIView
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404

from common.mixins import IDInFilterMixin
from common.permissions import IsSuperUserOrAppUser, IsValidUser
from .models import Database, Table, Field, TransferSchedule, Command
from .serializers import DatabaseSerializer, TableSerializer, FieldSerializer, ScheduleSerializer, CommandSerializer


class DatabaseViewSet(IDInFilterMixin, BulkModelViewSet):
    filter_fields = ("name", "dev", 'opr', 'bus', 'comment')
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
    filter_fields = ("database", "name", "dev", 'opr', 'bus', 'comment')
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


class ScheduleViewSet(viewsets.ModelViewSet):  # mixins.ListModelMixin, generics.GenericAPIView
    filter_fields = ("periodic", "type")
    search_fields = filter_fields
    ordering_fields = ("create_time", )
    queryset = TransferSchedule.objects.all()
    serializer_class = ScheduleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)
    http_method_names = ('get', )

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(creator=self.request.user)


class CommandViewSet(viewsets.ModelViewSet):
    filter_fields = ('schedule', 'table')
    ordering_fields = ("id",)
    search_fields = filter_fields
    queryset = Command.objects.all()
    serializer_class = CommandSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsValidUser,)
    http_method_names = ('get', )

    def get_queryset(self):
        return super().get_queryset()


class UserCommandViewSet(CommandViewSet):

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(schedule__creator=self.request.user)
