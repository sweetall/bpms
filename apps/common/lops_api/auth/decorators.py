from functools import wraps

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import available_attrs
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib.auth import authenticate, login

from common.lops_api.base import auth
from users.utils import get_login_ip
from users.tasks import write_login_log_async


def cookie_check(request):
    """
    Get user info by cookie.
    If cookie or user_info is None, redirect to login page.
    :param request:
    :return:
    """
    print('*' * 40 + 'Cookie check' + '*' * 40)
    _cookie = request.COOKIES.get(settings.LOPS_AUTH_COOKIE)
    if _cookie:
        if not request.user.is_authenticated:
            _, user_info = auth(_cookie)
            if user_info:
                user = authenticate(request, **user_info)
                print("User authenticate: %s" % user)
                login(request, user)

                # write login log
                login_ip = get_login_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                write_login_log_async.delay(
                    user.username, type='W',
                    ip=login_ip, user_agent=user_agent
                )

            else:
                print('Can not get user info by ticket: %s' % _cookie)
                return False
        print('User login...')
        return True


def user_passes_test(test_func, login_url=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.get_full_path()
            return redirect('%s?next=%s' % (settings.LOPS_LOGIN_URL, path))
        return _wrapped_view
    return decorator


def login_required(func=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary
    :param func:
    :return:
    """
    actual_decorator = user_passes_test(cookie_check)
    if func:
        return actual_decorator(func)
    return actual_decorator


if not settings.LOPS_AUTH:
    login_required = django_login_required
