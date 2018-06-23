#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from django.urls import path, re_path

from .. import views

app_name = 'terminal'

urlpatterns = [
    # Terminal view
    re_path(r'^terminal/$', views.TerminalListView.as_view(), name='terminal-list'),
    re_path(r'^terminal/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.TerminalDetailView.as_view(), name='terminal-detail'),
    re_path(r'^terminal/(?P<pk>[0-9a-zA-Z\-]{36})/connect/$', views.TerminalConnectView.as_view(), name='terminal-connect'),
    re_path(r'^terminal/(?P<pk>[0-9a-zA-Z\-]{36})/update/$', views.TerminalUpdateView.as_view(), name='terminal-update'),
    re_path(r'^(?P<pk>[0-9a-zA-Z\-]{36})/accept/$', views.TerminalAcceptView.as_view(), name='terminal-accept'),
    re_path(r'^web-terminal/$', views.WebTerminalView.as_view(), name='web-terminal'),

    # Session view
    re_path(r'^session-online/$', views.SessionOnlineListView.as_view(), name='session-online-list'),
    re_path(r'^session-offline/$', views.SessionOfflineListView.as_view(), name='session-offline-list'),
    re_path(r'^session/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.SessionDetailView.as_view(), name='session-detail'),

    # Command view
    re_path(r'^command/$', views.CommandListView.as_view(), name='command-list'),

]
