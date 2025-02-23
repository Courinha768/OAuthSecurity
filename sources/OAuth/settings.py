import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DJANGO_DEBUG', 'TRUE')
ALLOWED_HOSTS = [os.environ.get('DJANGO_ALLOWED_HOSTS', '*')]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'rest_framework',
    'rest_framework_simplejwt',

    'apps.authentication'
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
DEFAULT_USER_MODEL = 'authentication.User'

LOGGING = {
	'version': 1,
	'handlers': {
		'console': {
			'level': 'INFO',
			'class': 'logging.StreamHandler',
		},
	},
	'loggers': {
		'django': {
			'handlers': ['console'],
			'level': 'DEBUG',
			'propagate': True,
		},
		'authentication': {
			'handlers': ['console'],
			'level': 'DEBUG',
			'propagate': False,
		},
	},
}
