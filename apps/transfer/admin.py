from django.contrib import admin
from .models import Database, Table, Field
# Register your models here.


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota', 'is_active', 'dev', 'opr', 'comment')
    search_fields = ('name', )
    ordering = ('name', )
    readonly_fields = ('modifier', 'modify_time')


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'database', 'is_active', 'dev', 'opr', 'comment')
    search_fields = ('name', )
    ordering = ('name', )
    readonly_fields = ('modifier', 'modify_time')


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'table', 'type', 'comment')
    search_fields = ('name', )
    ordering = ('name', )
    readonly_fields = ('modifier', 'modify_time')
