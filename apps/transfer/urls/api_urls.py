from django.urls import path, re_path
from .. import api
from rest_framework_bulk.routes import BulkRouter
app_name = 'transfer'

router = BulkRouter()
router.register(r'databases', api.DatabaseViewSet, 'database')
router.register(r'tables', api.TableViewSet, 'table')
router.register(r'fields', api.FieldViewSet, 'field')
router.register(r'schedules', api.ScheduleViewSet, 'schedule')
router.register(r'commands', api.CommandViewSet, 'command')
router.register(r'user_commands', api.UserCommandViewSet, 'user_command')

urlpatterns = [
    path('schedule/active/', api.active_transfer_task, name='transfer_task-active'),
    path('schedule/delete/', api.delete_transfer_task, name='transfer_task-delete')
]
urlpatterns += router.urls
