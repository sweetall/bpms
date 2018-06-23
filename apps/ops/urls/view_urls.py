# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals


from django.urls import path, re_path
from .. import views

__all__ = ["urlpatterns"]

app_name = "ops"

urlpatterns = [
    # TResource Task url
    re_path(r'^task/$', views.TaskListView.as_view(), name='task-list'),
    re_path(r'^task/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.TaskDetailView.as_view(), name='task-detail'),
    re_path(r'^task/(?P<pk>[0-9a-zA-Z\-]{36})/adhoc/$', views.TaskAdhocView.as_view(), name='task-adhoc'),
    re_path(r'^task/(?P<pk>[0-9a-zA-Z\-]{36})/history/$', views.TaskHistoryView.as_view(), name='task-history'),
    re_path(r'^adhoc/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.AdHocDetailView.as_view(), name='adhoc-detail'),
    re_path(r'^adhoc/(?P<pk>[0-9a-zA-Z\-]{36})/history/$', views.AdHocHistoryView.as_view(), name='adhoc-history'),
    re_path(r'^adhoc/history/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.AdHocHistoryDetailView.as_view(), name='adhoc-history-detail'),
    re_path(r'^celery/task/(?P<pk>[0-9a-zA-Z\-]{36})/log/$', views.CeleryTaskLogView.as_view(), name='celery-task-log'),
]
