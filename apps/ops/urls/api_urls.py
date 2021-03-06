# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals

from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from .. import api


app_name = "ops"

router = DefaultRouter()
router.register(r'v1/tasks', api.TaskViewSet, 'task')
router.register(r'v1/adhoc', api.AdHocViewSet, 'adhoc')
router.register(r'v1/history', api.AdHocRunHistorySet, 'history')

urlpatterns = [
    re_path(r'^v1/tasks/(?P<pk>[0-9a-zA-Z\-]{36})/run/$', api.TaskRun.as_view(), name='task-run'),
    re_path(r'^v1/celery/task/(?P<pk>[0-9a-zA-Z\-]{36})/log/$', api.CeleryTaskLogApi.as_view(), name='celery-task-log'),

    path('v1/celery/periodic_task/active/', api.active_task, name='periodic_task-active'),
    path('v1/celery/periodic_task/delete/', api.delete_task, name='periodic_task-delete')
]

urlpatterns += router.urls
