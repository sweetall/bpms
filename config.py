"""
    bpms.config
    ~~~~~~~~~~~~~~~~~

    Jumpserver project setting file

    :copyright: (c) 2014-2017 by Jumpserver Team
    :license: GPL v2, see LICENSE for more details.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Use it to encrypt or decrypt data
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.environ.get('SECRET_KEY') or '2vym+ky!997d5kkcc64mnz06y1mmui3lut#(^wd=%s_qj$1%x'

    # Django security setting, if your disable debug model, you should setting that
    ALLOWED_HOSTS = ['*']

    # Development env open this, when error occur display the full process track, Production disable it
    # DEBUG = True

    # DEBUG, INFO, WARNING, ERROR, CRITICAL can set. See https://docs.djangoproject.com/en/1.10/topics/logging/
    LOG_LEVEL = 'DEBUG'
    LOG_DIR = os.path.join(BASE_DIR, 'logs')

    # Database setting, Support sqlite3, mysql, postgres ....
    # See https://docs.djangoproject.com/en/1.10/ref/settings/#databases

    # SQLite setting:
    DB_ENGINE = 'sqlite3'
    DB_NAME = os.path.join(BASE_DIR, 'data', 'db.sqlite3')

    # MySQL or postgres setting like:
    # DB_ENGINE = 'mysql'
    # DB_HOST = '127.0.0.1'
    # DB_PORT = 3306
    # DB_USER = 'root'
    # DB_PASSWORD = ''
    # DB_NAME = 'bpms'

    # When Django start it will bind this host and port
    # ./manage.py runserver 127.0.0.1:8080
    HTTP_BIND_HOST = '0.0.0.0'
    HTTP_LISTEN_PORT = 8080

    # Use Redis as broker for celery and web socket
    REDIS_HOST = '127.0.0.1'  # '172.18.114.199'  # 39.108.211.151 '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PASSWORD = ''
    BROKER_URL = 'redis://%(password)s%(host)s:%(port)s/3' % {
        'password': REDIS_PASSWORD,
        'host': REDIS_HOST,
        'port': REDIS_PORT,
    }

    # Email settings
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_SSL = True  # 465
    EMAIL_USE_TLS = False  # 587
    EMAIL_HOST = 'smtp.sina.com'
    EMAIL_PORT = 465
    EMAIL_HOST_USER = 'sweet_all@sina.com'
    EMAIL_HOST_PASSWORD = '1234Qwer'
    DEFAULT_FROM_EMAIL = 'sweet_all@sina.com'
    # EMAIL_FROM = 'sweet_all@sina.com'
    EMAIL_SUBJECT_PREFIX = '[BPMS]'
    EMAIL_TIMEOUT = 10

    def __init__(self):
        pass

    def __getattr__(self, item):
        return None


class DevelopmentConfig(Config):
    DEBUG = True
    ADMINS = (('时文涛', 'sweetalltt@yahoo.com'),)

    LOPS_AUTH = False
    LOPS_HOST = 'http://127.0.0.1'


class TestConfig(Config):
    pass


class ProductionConfig(Config):
    pass


# Default using Config settings, you can write if/else for different env
config = DevelopmentConfig()

