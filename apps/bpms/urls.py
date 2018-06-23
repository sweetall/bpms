"""bpms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import unicode_literals

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

from .views import IndexView, LunaView

from common.lops_api.auth.urls import required
from common.lops_api.auth.decorators import login_required

schema_view = get_schema_view(url='/', title='Users API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    path('bpms/admin/', admin.site.urls),
]

if settings.LOPS_AUTH:
    urlpatterns += required(login_required, [
        path('bpms/', IndexView.as_view(), name='index'),
        path('bpms/luna/', LunaView.as_view(), name='luna-error'),
        path('bpms/users/', include('users.urls.views_urls', namespace='users')),
        path('bpms/assets/', include('assets.urls.views_urls', namespace='assets')),
        path('bpms/perms/', include('perms.urls.views_urls', namespace='perms')),
        path('bpms/terminal/', include('terminal.urls.views_urls', namespace='terminal')),
        path('bpms/ops/', include('ops.urls.view_urls', namespace='ops')),
        path('bpms/audits/', include('audits.urls.view_urls', namespace='audits')),
        path('bpms/settings/', include('common.urls.view_urls', namespace='settings')),
        path('bpms/common/', include('common.urls.view_urls', namespace='common')),

        path('bpms/transfer/', include('transfer.urls.view_urls', namespace='transfer')),

        # Api url view map

        # External apps url
        path('bpms/captcha/', include('captcha.urls')),
    ])
else:
    urlpatterns += [
        path('bpms/', IndexView.as_view(), name='index'),
        path('bpms/luna/', LunaView.as_view(), name='luna-error'),
        path('bpms/users/', include('users.urls.views_urls', namespace='users')),
        path('bpms/assets/', include('assets.urls.views_urls', namespace='assets')),
        path('bpms/perms/', include('perms.urls.views_urls', namespace='perms')),
        path('bpms/terminal/', include('terminal.urls.views_urls', namespace='terminal')),
        path('bpms/ops/', include('ops.urls.view_urls', namespace='ops')),
        path('bpms/audits/', include('audits.urls.view_urls', namespace='audits')),
        path('bpms/settings/', include('common.urls.view_urls', namespace='settings')),
        path('bpms/common/', include('common.urls.view_urls', namespace='common')),

        path('bpms/transfer/', include('transfer.urls.view_urls', namespace='transfer')),

        # Api url view map

        # External apps url
        path('bpms/captcha/', include('captcha.urls')),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
            + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += [
    # Api url view map
    path('bpms/api/users/', include('users.urls.api_urls', namespace='api-users')),
    path('bpms/api/assets/', include('assets.urls.api_urls', namespace='api-assets')),
    path('bpms/api/perms/', include('perms.urls.api_urls', namespace='api-perms')),
    path('bpms/api/terminal/', include('terminal.urls.api_urls', namespace='api-terminal')),
    path('bpms/api/ops/', include('ops.urls.api_urls', namespace='api-ops')),
    path('bpms/api/audits/', include('audits.urls.api_urls', namespace='api-audits')),
    path('bpms/api/common/', include('common.urls.api_urls', namespace='api-common')),

    path('bpms/api/transfer/', include('transfer.urls.api_urls', namespace='api-transfer')),
]

if settings.DEBUG:
    urlpatterns += [
        path('bpms/docs/', schema_view, name="docs"),
    ]

