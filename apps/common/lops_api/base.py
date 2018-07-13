import requests
import logging

from django.core.mail import send_mail as send_mail_def


from django.conf import settings

logger = logging.getLogger('bpms')


def auth(token):
    payload = {'key': token}
    try:
        r = requests.post(settings.LOPS_AUTH_API, data=payload)
        data = r.json()
        if data['status']:
            user_info = data['data']
            return True, user_info
        return False, False
    except Exception as err:
        logger.error(err, exc_info=True)
        return False, False


def send_mail(subject, message, from_email, recipient_list, cc_list=None, html_message=None):
    to = ','.join(recipient_list)
    cc = ','.join(cc_list) if cc_list else None
    if not to:
        return {'status': False, 'message': 'Recipient_list can not be none!'}
    payload = {
        'subject': subject,
        'message': message,
        'to': to,
        'cc': cc,
        'html': html_message,
        'from_email': from_email
    }
    try:
        r = requests.post(settings.LOPS_EMAIL_API, data=payload)
        data = r.json()
        if data['status']:
            return {'status': True, 'message': 'Send email successfully.'}
        else:
            logger.error('send email fail: %s' % data['message'], exc_info=True)
            return {'status': False, 'message': 'send email fail: %s' % data['message']}
    except Exception as err:
        logger.error(err, exc_info=True)
        return {'status': False, 'message': str(err)}


if not settings.LOPS_AUTH:
    send_mail = send_mail_def
