# -*- encoding: utf-8 -*-
# Django settings for merengue project.

from os import path
from merengue import settings as merengue_settings

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
ADMIN_MEDIA_PREFIX = '/media_admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'v$*k)ri8i*yv@yb2w!c)t#aj$o=na8u#855#wsve4!iw%u__hy'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'merengue.themes.loader.load_template_source', # for enabling theme support in Merengue
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'merengue.context_processors.all_context',
    'merengue.themes.context_processors.media',
    'merengue.section.context_processors.section',
)

MIDDLEWARE_CLASSES = (
    'cmsutils.middleware.I18NUpdateCacheMiddleware', # this has to be first
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'merengue.middleware.RemoveRandomAjaxParameter',
    'merengue.section.middleware.SectionMiddleware',
    'merengue.section.middleware.DebugSectionMiddleware',
    'merengue.middleware.SimplifiedLayoutMiddleware',
    'cmsutils.middleware.AutomatizedTestingMiddleware',
    'merengue.plug.middleware.ActivePluginsMiddleware',
    #'django.middleware.gzip.GZipMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'cmsutils.middleware.I18NFetchFromCacheMiddleware', # this has to be last
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

ROOT_URLCONF = 'merengueproj.urls'

TEMPLATE_DIRS = (
    path.join(BASEDIR, 'templates'),
)

PLUGINS_DIR = 'plugins'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/cuentas/entrar/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.gis',
    'django_extensions',
    'debug_toolbar',
    'template_utils',
    'batchadmin',
    'cmsutils',
    'transmeta',
    'rosetta',
    'tagging',
    'sorl.thumbnail',
    'pagination',
    'inplaceeditform',
    'searchform',
    'inlinetrans',
    'mptt',
    'tinyimages',
    'rating',
    'threadedcomments',
    'captcha',
    'south',
) + merengue_settings.MERENGUE_APPS

TEST_RUNNER = 'merengue.test.run_tests'
TEST_DB_CREATION_SUFFIX = 'WITH TEMPLATE template_postgis'

FIXTURE_DIRS = (
    path.join(BASEDIR, 'fixtures', 'base'),
)

FIXTURES_EXCLUDES = (
    'auth.permission',
)

DOCUMENT_STATUS_LIST = (
    (1, ugettext('Draft')),
    (2, ugettext('Published')),
)

STATUS_LIST = (
    ('draft', ugettext('Borrador')),
    ('pending', ugettext('Pendiente')),
    ('published', ugettext('Publicado')),
    ('pasive', ugettext('Registro pasivo')),
    ('deleted_in_plone', ugettext('Borrado en Plone')),
)

BUILDBOT_IP = '192.168.11.209'
INTERNAL_IPS = ('127.0.0.1', '80.36.82.38', BUILDBOT_IP)

# Google API Key for localhost:8000
# http://code.google.com/apis/maps/signup.html
GOOGLE_MAPS_API_KEY = 'ABQIAAAAddxuy_lt2uAk9Y30XD3MJhQCULP4XOMyhPd8d_NrQQEO8sT8XBRRmJjQjU4qrycwOKb_v70y1h_1GQ'
GOOGLE_MAPS_API_VERSION = '3.x'
DEFAULT_LATITUDE = 36.851362
DEFAULT_LONGITUDE = -5.753321

FILTRABLE_MODELS = (
)

# Pagination options
PAGE_VARIABLE = 'page'

LIMIT_URL_SPIDER_TEST = 20

# Overwrite options tinyMCE
EXTRA_MCE = {
'theme_advanced_buttons1': 'bold,italic,copy,paste,pasteword,underline,justifyleft,justifycenter,justifyright,justifyfull,bullist,numlist,outdent,indent',
}

TINYMCE_MEDIA = MEDIA_URL + "cmsutils/js/widgets/tiny_mce/"

SEARCHBAR_MIN_RESULTS = 5

BATCHADMIN_MEDIA_PREFIX= ''
BATCHADMIN_JQUERY_JS= 'js/jquery-1.2.6.min.js'

LOGOUT_PROTECTED_URL_REDIRECTS = (
    #(r'^/regularexpresion/(.*)$', '/redirect_url'),
)

CACHE_BACKEND = 'locmem:///'
CACHE_MIDDLEWARE_SECONDS = 3600*24
CACHE_MIDDLEWARE_KEY_PREFIX = 'merengue'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# It also can be JaroWinkler
SEARCH_ALGORITHM = 'LevenshteinDistance'
PROPERTIES_JAROWINKLER = {'accuracy': 0.75, 'weight': 0.05}
PROPERTIES_LEVENTEIN = {'accuracy_letter': 3}

SVNDIR = path.join(BASEDIR, 'apps')

PRODUCTION_DB_URL = ""
PRODUCTION_DB_UPDATE_PASSWORDS = (('admin', 'admin'), )

# For rosetta
ENABLE_TRANSLATION_SUGGESTIONS = False

DEFAULT_FROM_EMAIL = 'no-reply@yaco.es'
SUGGESTION_BOX_EMAIL = 'info@yaco.es'

CONTACT_SUGGESTIONBOX_PREFIX = 'SUGGESTION BOX'

CAPTCHA_SETTINGS = {
    'NUMBER_SWAP': {
                    'O': '0',
                    'Z': '2',
                    'S': '5',
                    'B': '8',
    },
    'CASE_SENSITIVE': False,
}

# Allow overwriting any configuration in optional settings_local.py
# (it can be used to set up your own database, debug and cache options, contact mails...)
try:
    from settings_local import *
except ImportError:
    pass
