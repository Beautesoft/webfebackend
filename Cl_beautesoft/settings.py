"""
Django settings for Cl_beautesoft project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0hvkn)58&z=%mogc(sz!324jk5-g4pp*8q=7$g(g7lvb3b(^hf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['52.60.58.9','127.0.0.1','103.253.15.184','103.253.15.185','UBUNTUCLOUD15-185']



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'mathfilters',
    'corsheaders',
    'cl_table',
    'cl_app',
    'custom',
]

MIDDLEWARE = [
    'Cl_beautesoft.middleware1.open_access_middleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',

]

ROOT_URLCONF = 'Cl_beautesoft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'Cl_beautesoft.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

#postgres
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'beautesoft_db',
#         'USER': 'admin',
#         'PASSWORD': 'Doodle@123',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

#microsoft sql client server
# DATABASES = {
#     'default': {
#         'ENGINE': 'sql_server.pyodbc',
#         'NAME': 'BioSkin_TPN_Tampines_20200904',
#         'HOST': 'sequoiademo.ddns.net',
#         'PORT': '1435',
#         'USER': 'sa',
#         'PASSWORD': 'bigtree',
#         'OPTIONS': {
#             'driver': 'ODBC Driver 17 for SQL Server',
#         }
#     }
# }

# #microsoft sql local server
# DATABASES = {
#     'default': {
#         'ENGINE': 'sql_server.pyodbc',
#         'NAME': 'sittest',
#         'HOST': 'localhost',
#         'PORT': '1433',
#         'USER': 'sa',
#         'PASSWORD': 'Doodle@123',
#         'OPTIONS': {
#             'driver': 'ODBC Driver 17 for SQL Server',
#         }
#     }
# }


# # # normal db
# DATABASES = {
#     'default': {
#         'ENGINE': 'sql_server.pyodbc',
#         'NAME': 'healspahqtrain',
#         # 'NAME': 'MidysonTrain',
#         'HOST': '103.253.15.184',
#         'PORT': '1433',
#         'USER': 'sa',
#         'PASSWORD': 'Doodle@123',
#         'OPTIONS': {
#             'driver': 'ODBC Driver 17 for SQL Server',
#         }
#     }
# }


# # KPI db with real data.
DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'JeanYipBeauty_JYHQ',
        # 'NAME': 'MidysonTrain',
        'HOST': 'jeanyip.acy7lab.com',
        'PORT': '8890',
        'USER': 'zoonpavithra',
        'PASSWORD': 'Zoon24Python',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        }
    }
}

#mysql
# DATABASES =  {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'beautesoft_db',
#             'USER': 'root',
#             'PASSWORD': 'Doodle@123',
#             'HOST': '127.0.0.1',
#             'PORT': '3306',
#         }
#     }

REST_FRAMEWORK = {
   'DEFAULT_AUTHENTICATION_CLASSES': (
       'rest_framework.authentication.TokenAuthentication',
   ),
   'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.AllowAny',
   ),
   'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']

}
  


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
#TIME_ZONE =  'Asia/Calcutta'
TIME_ZONE = 'Asia/Singapore'

USE_I18N = True

USE_L10N = True

#USE_TZ = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PDF_ROOT = MEDIA_ROOT + '/pdf/'

# CORS Settings
CORS_ALLOW_METHODS =['DELETE','GET','OPTIONS','PATCH','POST','PUT',]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    'http://localhost:8003',
    # 'http://3.6.59.208',
    
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_HOST_USER = 'monica.b@doodleblue.com'
EMAIL_HOST_PASSWORD = 'MonicaBhass$05'

SMS_SECRET_KEY = "JBSWY3DPEHPK3VAG"
SMS_ACCOUNT_SID = 'AC2d4568886585462a8f7dbd240e09dc7c'
SMS_AUTH_TOKEN = '55774b4bfa51688df9380670a364423a'
SMS_SENDER = "+12097193857"
