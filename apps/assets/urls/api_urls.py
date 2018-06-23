# coding:utf-8
from django.urls import path, re_path
from .. import api
from rest_framework_bulk.routes import BulkRouter

app_name = 'assets'


router = BulkRouter()
router.register(r'v1/assets', api.AssetViewSet, 'asset')
router.register(r'v1/admin-user', api.AdminUserViewSet, 'admin-user')
router.register(r'v1/system-user', api.SystemUserViewSet, 'system-user')
router.register(r'v1/labels', api.LabelViewSet, 'label')
router.register(r'v1/nodes', api.NodeViewSet, 'node')
router.register(r'v1/domain', api.DomainViewSet, 'domain')
router.register(r'v1/gateway', api.GatewayViewSet, 'gateway')

urlpatterns = [
    path('v1/assets-bulk/', api.AssetListUpdateApi.as_view(), name='asset-bulk-update'),
    re_path(r'^v1/system-user/(?P<pk>[0-9a-zA-Z\-]{36})/auth-info/', api.SystemUserAuthInfoApi.as_view(),
            name='system-user-auth-info'),
    re_path(r'^v1/assets/(?P<pk>[0-9a-zA-Z\-]{36})/refresh/$',
            api.AssetRefreshHardwareApi.as_view(), name='asset-refresh'),
    re_path(r'^v1/assets/(?P<pk>[0-9a-zA-Z\-]{36})/alive/$',
            api.AssetAdminUserTestApi.as_view(), name='asset-alive-test'),
    path('v1/assets/user-assets/',
         api.UserAssetListView.as_view(), name='user-asset-list'),
    re_path(r'^v1/admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/nodes/$',
            api.ReplaceNodesAdminUserApi.as_view(), name='replace-nodes-admin-user'),
    re_path(r'^v1/admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/auth/$',
            api.AdminUserAuthApi.as_view(), name='admin-user-auth'),
    re_path(r'^v1/admin-user/(?P<pk>[0-9a-zA-Z\-]{36})/connective/$',
            api.AdminUserTestConnectiveApi.as_view(), name='admin-user-connective'),
    re_path(r'^v1/system-user/(?P<pk>[0-9a-zA-Z\-]{36})/push/$',
            api.SystemUserPushApi.as_view(), name='system-user-push'),
    re_path(r'^v1/system-user/(?P<pk>[0-9a-zA-Z\-]{36})/connective/$',
            api.SystemUserTestConnectiveApi.as_view(), name='system-user-connective'),
    re_path(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/children/$', api.NodeChildrenApi.as_view(), name='node-children'),
    re_path(r'^v1/nodes/children/$', api.NodeChildrenApi.as_view(), name='node-children-2'),
    re_path(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/children/add/$', api.NodeAddChildrenApi.as_view(), name='node-add-children'),
    re_path(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/$', api.NodeAssetsApi.as_view(), name='node-assets'),
    re_path(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/add/$', api.NodeAddAssetsApi.as_view(), name='node-add-assets'),
    re_path(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/replace/$', api.NodeReplaceAssetsApi.as_view(), name='node-replace-assets'),
    re_path(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/assets/remove/$', api.NodeRemoveAssetsApi.as_view(), name='node-remove-assets'),
    re_path(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/refresh-hardware-info/$', api.RefreshNodeHardwareInfoApi.as_view(), name='node-refresh-hardware-info'),
    re_path(r'^v1/nodes/(?P<pk>[0-9a-zA-Z\-]{36})/test-connective/$', api.TestNodeConnectiveApi.as_view(), name='node-test-connective'),

    re_path(r'^v1/gateway/(?P<pk>[0-9a-zA-Z\-]{36})/test-connective/$', api.GatewayTestConnectionApi.as_view(), name='test-gateway-connective'),
]

urlpatterns += router.urls

