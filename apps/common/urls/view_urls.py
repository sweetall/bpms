from __future__ import absolute_import

from django.urls import path, re_path

from .. import views

app_name = 'common'

urlpatterns = [
    re_path(r'^$', views.BasicSettingView.as_view(), name='basic-setting'),
    re_path(r'^email/$', views.EmailSettingView.as_view(), name='email-setting'),
    re_path(r'^ldap/$', views.LDAPSettingView.as_view(), name='ldap-setting'),
    re_path(r'^terminal/$', views.TerminalSettingView.as_view(), name='terminal-setting'),
]
