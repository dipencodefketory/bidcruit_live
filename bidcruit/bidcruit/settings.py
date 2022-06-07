"""
Django settings for bidcruit project. test .behind commit test

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=c0+*^fe)t2b!zt14guyz1=9lx@jay2hv+sg$qo-)3ep-wl^c*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['161.35.63.66','bidcruit.com','www.bidcruit.com','https://bidcruit.com']
ALLOWED_HOSTS = ['139.59.9.2','www.bidcruit.com','bidcruit.com','staffomatix.bidcruit.com']
CORS_ORIGIN_ALLOW_ALL=True
CORS_ORIGIN_WHITELIST = ['http://127.0.0.1:3000']

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'access-control-allow-origin'
]
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}
INSTALLED_APPS = [
    'channels',
    'videochat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'django_select2',
    # 'django_social_share',
    'candidate',
    'agency',
    'crispy_forms',
    #'django_user_agents',
    #'corsheaders',
    'accounts',
    'company',
    'django_elasticsearch_dsl',
    'chat',
    'tinymce',
    'bootstrap3',
    'rest_framework',
    'notifications',
    'rest_apscheduler',
    'colorfield',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware'
]
X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'bidcruit.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'resume_react'),(os.path.join(BASE_DIR,'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
               # make your file entry here.
               'filter_tags': 'candidate.templatetags.candidate_extras',
                'custom_filters' :'company.templatetags.custom_filters',
                'agency_filter' :'agency.templatetags.agency_filter',
            }
        },
    },
]

#WSGI_APPLICATION = 'bidcruit.wsgi.application'
ASGI_APPLICATION = 'bidcruit.asgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
#
DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'timeline',
        'NAME': 'bidcruit06',
        'USER': 'postgres',
        'PASSWORD': 'Bidcruit*909#2707',
        'HOST': 'database-1.c65leiqqukeb.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]

DATA_UPLOAD_MAX_MEMORY_SIZE =  None


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DJANGO_NOTIFICATIONS_CONFIG = { 'USE_JSONFIELD': True}
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'

# Add these new lines
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'


#EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
#EMAIL_HOST = 'email-smtp.us-east-2.amazonaws.com'
#EMAIL_PORT = 465
#EMAIL_HOST_USER = 'AKIA2ZZRZQKHTPMV4H5N'
#EMAIL_HOST_PASSWORD = 'BIkzSIurTQYX/Q9kFQL8yB+oVqt+ecvb3kqenL1RlsIg'
#EMAIL_USE_TLS = True


EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'support@bidcruit.com'
EMAIL_HOST_PASSWORD = 'Virus#2707&909#'
EMAIL_PORT = 587


ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

AUTH_USER_MODEL = 'accounts.User'


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        # "ROUTING":"videochat.routing.websocket_urlpatterns",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
messages.DEBUG: 'alert-info',
messages.INFO: 'alert-info',
messages.SUCCESS: 'alert-success',
messages.WARNING: 'alert-warning',
messages.ERROR: 'alert-danger',
}


DJANGO_NOTIFICATIONS_CONFIG = { 'USE_JSONFIELD': True}
