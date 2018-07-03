from django.urls import path, re_path
from .. import api
from rest_framework_bulk.routes import BulkRouter
app_name = 'transfer'

router = BulkRouter()
router.register(r'databases', api.DatabaseViewSet, 'database')
router.register(r'tables', api.TableViewSet, 'table')
router.register(r'fields', api.FieldViewSet, 'field')
router.register(r'schedules', api.ScheduleViewSet, 'schedule')

urlpatterns = [

]
urlpatterns += router.urls
