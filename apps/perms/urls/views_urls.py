# coding:utf-8

from django.urls import path, re_path
from .. import views

app_name = 'perms'

urlpatterns = [
    re_path(r'^asset-permission$', views.AssetPermissionListView.as_view(), name='asset-permission-list'),
    re_path(r'^asset-permission/create$', views.AssetPermissionCreateView.as_view(), name='asset-permission-create'),
    re_path(r'^asset-permission/(?P<pk>[0-9a-zA-Z\-]{36})/update$', views.AssetPermissionUpdateView.as_view(), name='asset-permission-update'),
    re_path(r'^asset-permission/(?P<pk>[0-9a-zA-Z\-]{36})$', views.AssetPermissionDetailView.as_view(), name='asset-permission-detail'),
    re_path(r'^asset-permission/(?P<pk>[0-9a-zA-Z\-]{36})/delete$', views.AssetPermissionDeleteView.as_view(), name='asset-permission-delete'),
    re_path(r'^asset-permission/(?P<pk>[0-9a-zA-Z\-]{36})/user$', views.AssetPermissionUserView.as_view(), name='asset-permission-user-list'),
    re_path(r'^asset-permission/(?P<pk>[0-9a-zA-Z\-]{36})/asset$', views.AssetPermissionAssetView.as_view(), name='asset-permission-asset-list'),
]


