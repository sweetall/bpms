from __future__ import absolute_import

from django.urls import path, re_path

from .. import api

app_name = 'common'

urlpatterns = [
    re_path(r'^v1/mail/testing/$', api.MailTestingAPI.as_view(), name='mail-testing'),
    re_path(r'^v1/ldap/testing/$', api.LDAPTestingAPI.as_view(), name='ldap-testing'),
    re_path(r'^v1/django-settings/$', api.DjangoSettingsAPI.as_view(), name='django-settings'),
]
