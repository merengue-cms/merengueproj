# -*- encoding: utf-8 -*-

# Django settings for merengue project.

from os import path
from merengue.settings import *  # pyflakes:ignore

ugettext = lambda s: s  # dummy ugettext function, as said on django docs

BASEDIR = path.dirname(path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = DEBUG
HTTP_ERRORS_DEBUG = DEBUG
COMPRESS = not DEBUG  # JS and CSS compression

ADMINS = (
    ('Your Name', 'youremail@yourdomain.org'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                       # Or path to database file if using sqlite3.
        'USER': '',                       # Not used with sqlite3.
        'PASSWORD': '',                   # Not used with sqlite3.
        'HOST': '',                       # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                       # Set to empty string for default. Not used with sqlite3.
    }
}

for database in DATABASES.values():
    if database['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        database['OPTIONS'] = {
            'autocommit': True,
        }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', ugettext('English')),
    ('es', ugettext('Español')),
    ('it', ugettext('Italiano')),
)

URL_DEFAULT_LANG = LANGUAGE_CODE

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Localization
USE_L10N = True
FORMAT_MODULE_PATH = 'formats'

# PostGIS extension flag
USE_GIS = False

if USE_GIS:
    INSTALLED_APPS += ('django.contrib.gis', 'merengue.places', )
    if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
        DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
        TEST_DB_CREATION_SUFFIX = 'WITH TEMPLATE template_postgis'
    if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
        DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.mysql'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(BASEDIR, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# Set to True for enabling site caching for anonymous visitors
CACHE_SITE_FOR_ANONYMOUS = False

MIDDLEWARE_CLASSES = PRE_MERENGUE_MIDDLEWARE_CLASSES + MERENGUE_MIDDLEWARE_CLASSES + POST_MERENGUE_MIDDLEWARE_CLASSES + (
    # put here aditional middlewares
)

ROOT_URLCONF = '{{ project_name }}.urls'

TEMPLATE_DIRS = (
    path.join(BASEDIR, 'templates'),
) + TEMPLATE_DIRS


INSTALLED_APPS += (
    # put here your project django apps
    'website',
)

FIXTURE_DIRS = (
    path.join(BASEDIR, 'fixtures', ),
)

SITE_FIXTURES = {
    # Site fixtures that will be loaded after data migration. Syntax:
    # 'app_name': ('fixture1', 'fixture2', ...)
}

INTERNAL_IPS = ('127.0.0.1', )

# Pagination options
LIMIT_URL_SPIDER_TEST = 20

# Overwrite options tinyMCE
TINYMCE_MEDIA = MEDIA_URL + "cmsutils/js/widgets/tiny_mce/"

TINYMCE_EXTRA_MEDIA = {
   'js': [],
   'css': [],
}

PRODUCTION_DB_URL = ""
PRODUCTION_DB_UPDATE_PASSWORDS = (('admin', 'admin'), )

# For johnny cache. Johnny cache key prefix should not be the same in other projects
CACHES = {
    'default': {
        'BACKEND': 'johnny.backends.locmem.LocMemCache',
        'KEY_PREFIX': SECRET_KEY,
        'OPTIONS': {
            'MAX_ENTRIES': 3000,
        },
    }
}
JOHNNY_MIDDLEWARE_KEY_PREFIX = '%s-cache' % DATABASES['default']['NAME']

# if merengue will detect new plugins in file system
DETECT_NEW_PLUGINS = False
# if merengue will detect broken plugins
DETECT_BROKEN_PLUGINS = True

# it merengue will send an email if there are some task to review
SEND_MAIL_IF_PENDING = False

DEBUG_TOOLBAR_PANELS = (
    #'debug_toolbar.panels.version.VersionDebugPanel',
    #'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    #'debug_toolbar.panels.sql.SQLDebugPanel',
    #'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    #'debug_toolbar.panels.logger.LoggingPanel',
    'merengue.dbtoolbar.BlockDebugPanel',
)

# File maximum size
# You can restrict the maximum size of uploaded files using
# MERENGUE_MAX_FILE_SIZE for any type of file or
# MERENGUE_MAX_IMAGE_SIZE for image files.
# You can use one, both or neither
#
#MERENGUE_MAX_FILE_SIZE = 10485760  # 10Mb
#MERENGUE_MAX_IMAGE_SIZE = 5242880  # 5Mb

# Allow overwriting any configuration in optional settings_local.py
# (it can be used to set up your own database, debug and cache options, contact mails...)
try:
    from settings_local import *
except ImportError:
    pass
