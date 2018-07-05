# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals


from django.urls import path, re_path
from transfer.views import database, table, field, schedule, command

__all__ = ["urlpatterns"]

app_name = "transfer"

urlpatterns = [
    path('database/', database.DatabaseListView.as_view(), name='database-list'),
    path('database/create/', database.DatabaseCreateView.as_view(), name='database-create'),
    path('database/<str:pk>/update/', database.DatabaseUpdateView.as_view(), name='database-update'),
    path('database/update/', database.DatabaseBulkUpdateView.as_view(), name='database-bulk-update'),

    path('database/<str:pk>/table/', table.TableListView.as_view(), name='table-list'),
    path('database/<str:pk>/table/create/', table.TableCreateView.as_view(), name='table-create'),
    path('database/<str:db_id>/table/<str:pk>/update/', table.TableUpdateView.as_view(), name='table-update'),
    path('database/<str:pk>/table/update/', table.TableBulkUpdateView.as_view(), name='table-bulk-update'),

    path('table/<str:pk>/filed/', field.FieldListView.as_view(), name='field-list'),
    path('table/<str:pk>/filed/create/', field.FieldCreateView.as_view(), name='field-create'),
    path('table/<str:tb_id>/filed/<str:pk>/update/', field.FieldUpdateView.as_view(), name='field-update'),
    path('table/<str:pk>/filed/update/', field.FieldBulkUpdateView.as_view(), name='field-bulk-update'),

    path('database/export/', database.DatabaseExportView.as_view(), name='database-export'),
    path('database/import/', database.DatabaseBulkImportView.as_view(), name='database-import'),

    path('schedule-import/', schedule.ImportScheduleListView.as_view(), name='schedule-import-list'),
    path('schedule-import/create/', schedule.ImportScheduleCreateView.as_view(), name='schedule-import-create'),
    path('schedule-import/<str:pk>/update/', schedule.ImportScheduleUpdateView.as_view(), name='schedule-import-update'),

    path('schedule-export/', schedule.ExportScheduleListView.as_view(), name='schedule-export-list'),
    path('schedule-export/create/', schedule.ExportScheduleCreateView.as_view(), name='schedule-export-create'),
    path('schedule-export/<str:pk>/update/', schedule.ExportScheduleUpdateView.as_view(), name='schedule-export-update'),

    path('command/', command.CommandListView.as_view(), name='command-list'),
]
