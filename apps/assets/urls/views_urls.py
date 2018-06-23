# coding:utf-8
from django.urls import path, re_path
from .. import views

app_name = 'assets'

urlpatterns = [
    # Resource asset url
    re_path(r'^$', views.AssetListView.as_view(), name='asset-index'),
    re_path(r'^asset/$', views.AssetListView.as_view(), name='asset-list'),
    re_path(r'^asset/create/$', views.AssetCreateView.as_view(), name='asset-create'),
    re_path(r'^asset/export/$', views.AssetExportView.as_view(), name='asset-export'),
    re_path(r'^asset/import/$', views.BulkImportAssetView.as_view(), name='asset-import'),
    re_path(r'^asset/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.AssetDetailView.as_view(), name='asset-detail'),
    re_path(r'^asset/(?P<pk>[0-9a-zA-Z\-]{36})/update/$', views.AssetUpdateView.as_view(), name='asset-update'),
    re_path(r'^asset/(?P<pk>[0-9a-zA-Z\-]{36})/delete/$', views.AssetDeleteView.as_view(), name='asset-delete'),
    re_path(r'^asset/update/$', views.AssetBulkUpdateView.as_view(), name='asset-bulk-update'),

    # User asset view
    re_path(r'^user-asset/$', views.UserAssetListView.as_view(), name='user-asset-list'),

    # Resource admin user url
    re_path(r'^admin-user/$', views.AdminUserListView.as_view(), name='admin-user-list'),
    re_path(r'^admin-user/create/$', views.AdminUserCreateView.as_view(), name='admin-user-create'),
    re_path(r'^admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    re_path(r'^admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/update/$', views.AdminUserUpdateView.as_view(), name='admin-user-update'),
    re_path(r'^admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/delete/$', views.AdminUserDeleteView.as_view(), name='admin-user-delete'),
    re_path(r'^admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/assets/$', views.AdminUserAssetsView.as_view(), name='admin-user-assets'),

    # Resource system user url
    re_path(r'^system-user/$', views.SystemUserListView.as_view(), name='system-user-list'),
    re_path(r'^system-user/create/$', views.SystemUserCreateView.as_view(), name='system-user-create'),
    re_path(r'^system-user/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.SystemUserDetailView.as_view(), name='system-user-detail'),
    re_path(r'^system-user/(?P<pk>[0-9a-zA-Z\-]{36})/update/$', views.SystemUserUpdateView.as_view(), name='system-user-update'),
    re_path(r'^system-user/(?P<pk>[0-9a-zA-Z\-]{36})/delete/$', views.SystemUserDeleteView.as_view(), name='system-user-delete'),
    re_path(r'^system-user/(?P<pk>[0-9a-zA-Z\-]{36})/asset/$', views.SystemUserAssetView.as_view(), name='system-user-asset'),

    re_path(r'^label/$', views.LabelListView.as_view(), name='label-list'),
    re_path(r'^label/create/$', views.LabelCreateView.as_view(), name='label-create'),
    re_path(r'^label/(?P<pk>[0-9a-zA-Z\-]{36})/update/$', views.LabelUpdateView.as_view(), name='label-update'),
    re_path(r'^label/(?P<pk>[0-9a-zA-Z\-]{36})/delete/$', views.LabelDeleteView.as_view(), name='label-delete'),

    re_path(r'^domain/$', views.DomainListView.as_view(), name='domain-list'),
    re_path(r'^domain/create/$', views.DomainCreateView.as_view(), name='domain-create'),
    re_path(r'^domain/(?P<pk>[0-9a-zA-Z\-]{36})/$', views.DomainDetailView.as_view(), name='domain-detail'),
    re_path(r'^domain/(?P<pk>[0-9a-zA-Z\-]{36})/update/$', views.DomainUpdateView.as_view(), name='domain-update'),
    re_path(r'^domain/(?P<pk>[0-9a-zA-Z\-]{36})/delete/$', views.DomainDeleteView.as_view(), name='domain-delete'),
    re_path(r'^domain/(?P<pk>[0-9a-zA-Z\-]{36})/gateway/$', views.DomainGatewayListView.as_view(), name='domain-gateway-list'),

    re_path(r'^domain/(?P<pk>[0-9a-zA-Z\-]{36})/gateway/create/$', views.DomainGatewayCreateView.as_view(), name='domain-gateway-create'),
    re_path(r'^domain/gateway/(?P<pk>[0-9a-zA-Z\-]{36})/update/$', views.DomainGatewayUpdateView.as_view(), name='domain-gateway-update'),
]

