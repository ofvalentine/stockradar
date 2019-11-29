import os
import django_heroku
import environs

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
is_production = os.environ.get('IS_HEROKU', None)

if is_production:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    DATABASES = {"default": os.environ.get("DATABASE_URL")}
else:
    env = environs.Env()
    env.read_env()
    DEBUG = TEMPLATE_DEBUG = env.bool("DEBUG", default=False)
    SECRET_KEY = env.str("SECRET_KEY")
    DATABASES = {"default": env.dj_db_url("DATABASE_URL", ssl_require=not DEBUG)}

ALLOWED_HOSTS = ['stockradar.herokuapp.com', '*']

INSTALLED_APPS = [
    'json_tag',
    'rest_framework',
    'index',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'stockradar.urls'

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

WSGI_APPLICATION = 'stockradar.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'index/static/')]

django_heroku.settings(locals())
