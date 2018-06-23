# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals


from django.urls import path, re_path
from .. import views

__all__ = ["urlpatterns"]

app_name = "audits"

urlpatterns = [
    re_path(r'^ftp-log/$', views.FTPLogListView.as_view(), name='ftp-log-list'),
]
