# -*- encoding: utf-8 -*-
# Django settings for merengue project.

from os import path
from merengue.settings import *

ugettext = lambda s: s # dummy ugettext function, as said on django docs

BASEDIR = path.dirname(path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Manuel Saelices', 'msaelices@yaco.es'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'merengue'             # Or path to database file if using sqlite3.
DATABASE_USER = 'merengue'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

LANGUAGES = (
    ('es', ugettext('Español')),
    ('en', ugettext('English')),
    ('fr', ugettext('Français')),
)

TRANSMETA_DEFAULT_LANGUAGE = 'es'

SITE_ID = 1
SITE_REGISTER_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

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
SECRET_KEY = 'v$*k)ri8i*yv@yb2w!c)t#aj$o=na8u#855#wsve4!iw%u__hy'

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    # put here aditional middlewares
)

DEBUG_TOOLBAR_PANELS = (
    #'debug_toolbar.panels.version.VersionDebugPanel',
    #'debug_toolbar.panels.timer.TimerDebugPanel',
    #'debug_toolbar.panels.headers.HeaderDebugPanel',
    #'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    #'debug_toolbar.panels.sql.SQLDebugPanel',
    #'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    #'debug_toolbar.panels.logger.LoggingPanel',
)

ROOT_URLCONF = '{{ project_name }}.urls'

TEMPLATE_DIRS = (
    path.join(BASEDIR, 'templates'),
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'

INSTALLED_APPS += (
    # put here your project django apps
)

SVNDIR = path.join(BASEDIR, 'apps')

TEST_RUNNER = 'merengue.test.run_tests'
TEST_DB_CREATION_SUFFIX = 'WITH TEMPLATE template_postgis'

FIXTURE_DIRS = (
    path.join(BASEDIR, 'fixtures', 'base'),
)

FIXTURES_EXCLUDES = (
    'auth.permission',
)

BUILDBOT_IP = '192.168.11.209'
INTERNAL_IPS = ('127.0.0.1', '80.36.82.38', BUILDBOT_IP)

# Pagination options
LIMIT_URL_SPIDER_TEST = 20

# Overwrite options tinyMCE
TINYMCE_MEDIA = MEDIA_URL + "cmsutils/js/widgets/tiny_mce/"

SEARCHBAR_MIN_RESULTS = 5

BATCHADMIN_MEDIA_PREFIX= ''
BATCHADMIN_JQUERY_JS= 'js/jquery-1.2.6.min.js'

LOGOUT_PROTECTED_URL_REDIRECTS = (
    #(r'^/regularexpresion/(.*)$', '/redirect_url'),
)

PRODUCTION_DB_URL = ""
PRODUCTION_DB_UPDATE_PASSWORDS = (('admin', 'admin'), )

# For rosetta
ENABLE_TRANSLATION_SUGGESTIONS = False

# Allow overwriting any configuration in optional settings_local.py
# (it can be used to set up your own database, debug and cache options, contact mails...)
try:
    from settings_local import *
except ImportError:
    pass
