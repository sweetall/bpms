import logging
import threading

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address


from django.contrib.auth.backends import ModelBackend

from users.models.user import User
from users.models.group import UserGroup

from .base import send_mail

logger = logging.getLogger('bpms')


class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages the api request network connection.
    """
    def __init__(self, api_url=None, timeout=None, **kwargs):
        super().__init__()
        self.api_url = api_url or settings.LOPS_EMAIL_API
        self.timeout = settings.EMAIL_TIMEOUT if timeout is None else timeout
        self._lock = threading.RLock()

    def open(self):
        """
        Ensure an open connection to the email server. Not need Return True.
        """
        return True

    def close(self):
        """Close the connection to the email server. not need, pass."""
        pass

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return
        with self._lock:
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message = email_message.message()
        an = email_message.alternatives
        html_message = an[0][0] if an else None
        cc = ','.join(email_message.cc)
        subject = email_message.subject

        result = send_mail(subject=subject, to=','.join(recipients), cc=cc, message=message, html=html_message,
                           from_email=from_email)
        return result['status']


class APIAuthBackend(ModelBackend):
    """
    API auth backend
    """

    def authenticate(self, request, **kwargs):
        username = kwargs.get('username')
        user_defaults = dict()
        user_defaults['username'] = username
        # user_defaults['password'] = kwargs.get('password')
        # user_defaults['first_name'] = kwargs.get('first_name', '')
        user_defaults['name'] = kwargs.get('name', '')
        user_defaults['email'] = kwargs.get('email', '')
        print(user_defaults)
        #
        # user_profile_defaults = dict()
        # user_profile_defaults['nickname'] = kwargs.get('nickname', '')
        # user_profile_defaults['signature'] = kwargs.get('signature', '')
        # user_profile_defaults['portrait'] = kwargs.get('portrait', '')
        # user_profile_defaults['job'] = kwargs.get('job', '')
        # user_profile_defaults['mold'] = kwargs.get('mold', '')
        # user_profile_defaults['phone'] = kwargs.get('phone', '')
        # user_profile_defaults['extension'] = kwargs.get('extension', '')
        # user_profile_defaults['is_on'] = kwargs.get('is_on', True)
        # user_profile_defaults['location'] = kwargs.get('location', '')

        # group_name = kwargs.get('deptid', '')
        #
        # group_profile_defaults = dict()
        # group_profile_defaults['name'] = kwargs.get('deptid_descr', '')
        # group_profile_defaults['name_short'] = kwargs.get('deptid_descr_short', '')
        # group_profile_defaults['level'] = kwargs.get('paic_deptno_desc', '')
        #
        # department_info = kwargs.get('branch', {})
        # department_defaults = dict()
        # department_defaults['name'] = department_info.get('name')
        # department_defaults['name_short'] = department_info.get('name_short')
        # department_defaults['code'] = department_info.get('code')
        # department_defaults['level'] = department_info.get('level')

        user, created = User.objects.update_or_create(username=username, defaults=user_defaults)
        # user_profile, _ = UserProfile.objects.update_or_create(user=user, defaults=user_profile_defaults)

        # if group_name:
        #     group, _ = Group.objects.get_or_create(name=group_name)
        #     group_profile, _ = GroupProfile.objects.update_or_create(group=group, defaults=group_profile_defaults)
        #     if department_defaults['code']:
        #         department, _ = Department.objects.update_or_create(code=department_defaults['code'],
        #                                                             defaults=department_defaults)
        #         group_profile.department = department
        #         group_profile.save()
        #     if user.userprofile.organize != group:
        #         user_profile.organize = group
        #         user_profile.save()
        #         user.groups.add(group)
        return user
