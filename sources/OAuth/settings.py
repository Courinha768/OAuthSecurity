import os
from datetime import timedelta
from pathlib import Path

from .traceID import TraceIDFilter

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DJANGO_DEBUG', 'FALSE')
ALLOWED_HOSTS = [os.environ.get('DJANGO_ALLOWED_HOSTS', '*')]
APPEND_SLASH=False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'health_check',
    'rest_framework_simplejwt',
    'django_redis',

    'apps.consumers',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

ROOT_URLCONF = 'OAuth.urls'
WSGI_APPLICATION = 'OAuth.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
		'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
		'HOST': os.environ.get('POSTGRES_HOST'),
		'PORT': os.environ.get('POSTGRES_PORT'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_USER_MODEL = 'consumers.Consumer'

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LOG_DIR = os.getenv('LOG_DIR', '/var/log/django')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} [{trace_id}] - {name} - {message}',
            'style': '{'
        },
        'json': {
			'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s", "trace_id": "%(trace_id)s"}',
			'class': 'logging.Formatter',
		},
    },
	'filters': {
        'trace_id_filter': {
            '()': TraceIDFilter,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['trace_id_filter'],
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django_app.log'),
            'formatter': 'verbose',
            'filters': ['trace_id_filter'],
        },
        'json_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django_app.json'),
            'formatter': 'json',
            'filters': ['trace_id_filter'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'json_file'],
            'level': LOG_LEVEL,
            'propagate': True,
        },
        'apps.consumers': {
            'handlers': ['console', 'file', 'json_file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

AUTHENTICATION_BACKENDS = [
    'apps.consumers.authentication.ConsumerSecretAuthBackend',
	'django.contrib.auth.backends.ModelBackend'
]

SIMPLE_JWT = {
	'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
	'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
	'ROTATE_REFRESH_TOKENS': True,
	'BLACKLIST_AFTER_ROTATION': True,
	'ALGORITHM': 'HS256',
	'SIGNING_KEY': SECRET_KEY,
}

REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
}

REDIS_HOST = os.getenv('REDIS_HOST', 'security-cache')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

CACHES = {
	'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
		'TIMEOUT': 300,
    },
	'fallback': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]
