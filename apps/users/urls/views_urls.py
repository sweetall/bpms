from __future__ import absolute_import

from django.urls import path, re_path
from .. import views

app_name = 'users'

urlpatterns = [
    # Login view
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),
    path('login/otp', views.UserLoginOtpView.as_view(), name='login-otp'),
    path('password/forgot', views.UserForgotPasswordView.as_view(), name='forgot-password'),
    path('password/forgot/sendmail-success', views.UserForgotPasswordSendmailSuccessView.as_view(), name='forgot-password-sendmail-success'),
    path('password/reset', views.UserResetPasswordView.as_view(), name='reset-password'),
    path('password/reset/success', views.UserResetPasswordSuccessView.as_view(), name='reset-password-success'),

    # Profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('profile/password/update/', views.UserPasswordUpdateView.as_view(), name='user-password-update'),
    path('profile/pubkey/update/', views.UserPublicKeyUpdateView.as_view(), name='user-pubkey-update'),
    path('profile/pubkey/generate/', views.UserPublicKeyGenerateView.as_view(), name='user-pubkey-generate'),
    path('profile/otp/enable/authentication/', views.UserOtpEnableAuthenticationView.as_view(), name='user-otp-enable-authentication'),
    path('profile/otp/enable/install-app/', views.UserOtpEnableInstallAppView.as_view(), name='user-otp-enable-install-app'),
    path('profile/otp/enable/bind/', views.UserOtpEnableBindView.as_view(), name='user-otp-enable-bind'),
    path('profile/otp/disable/authentication/', views.UserOtpDisableAuthenticationView.as_view(), name='user-otp-disable-authentication'),
    path('profile/otp/settings-success/', views.UserOtpSettingsSuccessView.as_view(), name='user-otp-settings-success'),

    # User view
    path('user', views.UserListView.as_view(), name='user-list'),
    path('user/export/', views.UserExportView.as_view(), name='user-export'),
    path('first-login/', views.UserFirstLoginView.as_view(), name='user-first-login'),
    path('user/import/', views.UserBulkImportView.as_view(), name='user-import'),
    path('user/create', views.UserCreateView.as_view(), name='user-create'),
    re_path(r'^user/(?P<pk>[0-9a-zA-Z\-]{36})/update$', views.UserUpdateView.as_view(), name='user-update'),
    path('user/update', views.UserBulkUpdateView.as_view(), name='user-bulk-update'),
    re_path(r'^user/(?P<pk>[0-9a-zA-Z\-]{36})$', views.UserDetailView.as_view(), name='user-detail'),
    re_path(r'^user/(?P<pk>[0-9a-zA-Z\-]{36})/assets', views.UserGrantedAssetView.as_view(), name='user-granted-asset'),
    re_path(r'^user/(?P<pk>[0-9a-zA-Z\-]{36})/login-history', views.UserDetailView.as_view(), name='user-login-history'),

    # User group view
    path('user-group', views.UserGroupListView.as_view(), name='user-group-list'),
    re_path(r'^user-group/(?P<pk>[0-9a-zA-Z\-]{36})$', views.UserGroupDetailView.as_view(), name='user-group-detail'),
    re_path(r'^user-group/create$', views.UserGroupCreateView.as_view(), name='user-group-create'),
    re_path(r'^user-group/(?P<pk>[0-9a-zA-Z\-]{36})/update$', views.UserGroupUpdateView.as_view(), name='user-group-update'),
    re_path(r'^user-group/(?P<pk>[0-9a-zA-Z\-]{36})/assets', views.UserGroupGrantedAssetView.as_view(), name='user-group-granted-asset'),

    # Login log
    path('login-log/', views.LoginLogListView.as_view(), name='login-log-list'),
]
