# -*- encoding: utf-8 -*-
# Django settings for andaluciaorg project.

from os import path

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
    'portal.context_processors.all_context',
    'section.context_processors.section',
)

MIDDLEWARE_CLASSES = (
    'cmsutils.middleware.I18NUpdateCacheMiddleware', # this has to be first
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'portal.middleware.PloneLocaleMiddleware',
    'portal.middleware.RemoveRandomAjaxParameter',
    'section.middleware.SectionMiddleware',
    'section.middleware.DebugSectionMiddleware',
    'portal.middleware.SimplifiedLayoutMiddleware',
    'cmsutils.middleware.AutomatizedTestingMiddleware',
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

ROOT_URLCONF = 'andaluciaorg.urls'

TEMPLATE_DIRS = (
    path.join(BASEDIR, 'templates'),
)

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
    'dmigrations',
    'cmsutils',
    'transmeta',
    'batchadmin',
    'jossoauth',
    'rosetta',
    'tagging',
    'sorl.thumbnail',
    'pagination',
    'multimedia',
    'places',
    'base',
    'portal',
    'golf',
    'beach',
    'restaurant',
    'shopping',
    'naturearea',
    'touristservice',
    'inplaceeditform',
    'inplaceeditchunks',
    'searchform',
    'certificate',
    'leisure',
    'visit',
    'accommodation',
    'event',
    'inlinetrans',
    'section',
    'mptt',
    'auto_reports',
    'reports',
    'help',
    'tinyimages',
    'rating',
    'internallinks',
    'favourites',
    'travelbook',
    'story',
    'threadedcomments',
    'convention',
    'sport',
    'healthandbeauty',
    'directions',
    'flamenco',
    'deal',
    'captcha',
    'profiles',
    'photocontests',
    'dataprovider',
    'route',
    'forums',
)

SECTION_MAP = {
    'alojamientos': {
        'class_names': ('accommodation', ),
        'app_name': 'accommodation',
        'published': True,
    },
    'certificados': {
        'class_names': tuple(),
        'app_name': 'certificate',
        'published': False,
    },
    'como-llegar': {
        'class_names': ('trainstation', 'airport', 'seaport', 'busstation', 'carrental', 'company'),
        'app_name': 'directions',
        'published': False,
    },
    'destinos': {
        'class_names': tuple(),
        'app_name': 'places',
        'published': True,
    },
    'espacios-naturales': {
        'class_names': ('naturearea', 'trail'),
        'app_name': 'naturearea',
        'published': True,
    },
    'eventos': {
        'class_names': ('event', ),
        'app_name': 'event',
        'published': True,
    },
    'flamenco': {
        'class_names': ('artist', 'flamencoplace', 'history'),
        'app_name': 'flamenco',
        'published': True,
    },
    'gastronomia': {
        'class_names': ('restaurant', ),
        'app_name': 'restaurant',
        'published': True,
    },
    'golf': {
        'class_names': ('course', ),
        'app_name': 'golf',
        'published': True,
    },
    'ocio-y-diversion': {
        'class_names': ('nightplace', 'park', 'shop'),
        'app_name': 'leisure',
        'published': True,
    },
    'ofertas': {
        'class_names': ('deal', ),
        'app_name': 'deal',
        'published': False,
    },
    'playas': {
        'class_names': ('beach', ),
        'app_name': 'beach',
        'published': True,
    },
    'reuniones-y-congresos': {
        'class_names': ('conventioncenter',
                        'conventionroom',
                        'conventioncompany',
                        'conventionboureau',
                        'baseconvention', ),
        'app_name': 'convention',
        'published': False,
    },
    'salud-y-belleza': {
        'class_names': ('habcenter', 'habtype', 'treatment', 'watertype' ),
        'app_name': 'healthandbeauty',
        'published': False,
    },
    'contacta-con-nosotros': {
        'class_names': ('touristinformation', ),
        'app_name': 'touristservice',
        'published': True,
    },
    'turismo-cultural': {
        'class_names': ('visit', ),
        'app_name': 'visit',
        'published': True,
    },
    'turismo-y-deporte': {
        'class_names': ('sportfacility', 'sport', 'marina', 'sportcategory'),
        'app_name': 'sport',
        'published': True,
    },
    'historias-de-andalucia': {
        'class_names': ('story', ),
        'app_name': 'story',
        'published': False,
    },
    'concurso-de-fotografia': {
        'class_names': ('contestant', 'contest', 'contestantcategory'),
        'app_name': 'photocontests',
        'published': False,
    },
    'cuaderno-de-viaje': {
        'class_names': tuple(),
        'app_name': 'travelbook',
        'published': True,
    },
    'rutas': {
        'class_names': ('route', 'routetype', 'routesubtype', 'itinerary'),
        'app_name': 'route',
        'published': False,
    },
}

LOGOUT_URLS_REVENT_REDIRECT = (
    (r'^/cuaderno-de-viaje/(.*)$', '/'),
)

# inverse mapping from SECTION_MAP, used for convenience
APP_SECTION_MAP = {}
for key, section in SECTION_MAP.items():
    for model_name in section['class_names']:
        APP_SECTION_MAP[model_name] = key

CLASS_NAMES_FOR_CAROUSEL = (
    'beach',
    'accommodation',
    'park',
    #'naturearea',
    'visit',
    'restaurant',
    'nightplace',
    'shop',
    'sportfacility',
    'marina',
)

CLASS_NAMES_FOR_PLACES = SortedDict((
    ('accommodation', ['accommodation']),
    ('beach', ['beach']),
    ('course', ['course']),
    ('event', ['event']),
    ('nightplace', ['nightplace']),
    ('park', ['park']),
    ('restaurant', ['restaurant']),
    ('shop', ['shop']),
    ('touristinformation', ['touristinformation']),
    ('visit', ['visit']),
    ('baseconvention', ['baseconvention', 'conventioncenter', 'conventioncompany', 'conventionroom', 'conventionboureau']),
    ('sport', ['sportfacility', 'marina']),
    ('flamenco', {'resource_model': 'base.basecontent',
                  'class_names': ['flamencoplace', 'shop', 'nightplace'],
                  'extra_or_filters': {'shop__shop_type__slug': 'flamenco', 'nightplace__nightplace_types__slug': 'tablao-flamenco',
                                       'class_name': 'flamencoplace'}}),
))

FEATURE_ALLOWED_TYPE =[('golf', 'course'),
                      ('beach', 'beach'),
                      ('restaurant', 'restaurant'),
                      ('shopping', 'shop'),
                      ('touristservice', 'touristinformation'),
                      ('naturearea', 'pointofinterest'),
                      ('naturearea', 'naturearea'),
                      ('leisure', 'nightplace'),
                      ('leisure', 'park'),
                      ('visit', 'visit'),
                      ('accommodation', 'accommodation'),
                      ('event', 'event'),
                      ('story', 'story'),
                      ('convention', 'conventioncenter'),
                      ('convention', 'conventionroom'),
                      ('convention', 'conventioncompany'),
                      ('convention', 'conventionboureau'),
                      ('sport', 'sportfacility'),
                      ('healthandbeauty', 'habcenter'),
                      ('directions', 'carrental'),
                      ('directions', 'airport'),
                      ('directions', 'seaport'),
                      ('directions', 'trainstation'),
                      ('directions', 'busstation'),
                      ('flamenco', 'artist'),
                      ('flamenco', 'flamencoplace'),
                      ('deal', 'deal'),
                      ('photocontests', 'contestant'),
                      ('route', 'route')]

TEST_RUNNER = 'portal.test.run_tests'
TEST_DB_CREATION_SUFFIX = 'WITH TEMPLATE template_postgis'

FIXTURE_DIRS = (
    path.join(BASEDIR, 'fixtures', 'auth'),
    path.join(BASEDIR, 'fixtures', 'sites'),
    path.join(BASEDIR, 'fixtures', 'places'),
    path.join(BASEDIR, 'fixtures', 'multimedia'),
    path.join(BASEDIR, 'fixtures', 'base'),
    path.join(BASEDIR, 'fixtures', 'inplaceeditchunks'),
    path.join(BASEDIR, 'fixtures', 'touristservice'),
    path.join(BASEDIR, 'fixtures', 'golf'),
    path.join(BASEDIR, 'fixtures', 'beach'),
    path.join(BASEDIR, 'fixtures', 'restaurant'),
    path.join(BASEDIR, 'fixtures', 'certificate'),
    path.join(BASEDIR, 'fixtures', 'naturearea'),
    path.join(BASEDIR, 'fixtures', 'leisure'),
    path.join(BASEDIR, 'fixtures', 'shopping'),
    path.join(BASEDIR, 'fixtures', 'visit'),
    path.join(BASEDIR, 'fixtures', 'accommodation'),
)

FIXTURES_EXCLUDES = (
    'auth.permission',
)

DOCUMENT_STATUS_LIST = (
    (1, ugettext('Borrador')),
    (2, ugettext('Publicado')),
)

PHOTOCONTEST_STATUS_LIST = DOCUMENT_STATUS_LIST

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
    'golf.course',
    'beach.beach',
    'restaurant.restaurant',
    'shopping.shop',
    'touristservice.touristinformation',
    # naturearea is unactived until naturearea section was published
    #'naturearea.naturearea.withbounds',
    'leisure.nightplace',
    'leisure.park',
    'visit.visit',
    'accommodation.accommodation',
    'event.event',
    'convention.baseconvention',
    'sport.sportfacility',
)

# Pagination options
PAGE_VARIABLE = 'page'
PAGINATION_DEFAULT_WINDOW = 3

LIMIT_URL_SPIDER_TEST = 20

# Overwrite options tinyMCE
EXTRA_MCE = {
'theme_advanced_buttons1': 'bold,italic,copy,paste,pasteword,underline,justifyleft,justifycenter,justifyright,justifyfull,bullist,numlist,outdent,indent',
}

TINYMCE_MEDIA = MEDIA_URL + "cmsutils/js/widgets/tiny_mce/"

SEARCHBAR_MIN_RESULTS = 5

BATCHADMIN_MEDIA_PREFIX= ''
BATCHADMIN_JQUERY_JS= 'js/jquery-1.2.6.min.js'

CACHE_BACKEND = 'dummy:///'
CACHE_MIDDLEWARE_SECONDS = 3600*24
CACHE_MIDDLEWARE_KEY_PREFIX = 'andaluciaorg'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

PLONE_LANGUAGE_COOKIE_NAME = 'I18N_LANGUAGE'

# It also can be JaroWinkler
SEARCH_ALGORITHM = 'LevenshteinDistance'
PROPERTIES_JAROWINKLER = {'accuracy': 0.75, 'weight': 0.05}
PROPERTIES_LEVENTEIN = {'accuracy_letter': 3}

DMIGRATIONS_DIR = path.join(BASEDIR, 'migrations')

SVNDIR = path.join(BASEDIR, 'apps')

PRODUCTION_DB_URL = "https://andalucia:andalucia06@trac.yaco.es/tur-andalucia/attachment/wiki/BasesDeDatos/backup_09073058.sql.bz2?format=raw"

PRODUCTION_DB_UPDATE_PASSWORDS = (('admin', 'andalucia06'), )

#Rosetta

ENABLE_TRANSLATION_SUGGESTIONS = False

DEFAULT_FROM_EMAIL = 'no-reply@andalucia.org'
DEALS_BCC_EMAIL = 'contenidos@andalucia.org'
SUGGESTION_BOX_EMAIL = 'contenidos@andalucia.org'

CONTACT_SUGGESTIONBOX_PREFIX = 'BUZON DE SUGERENCIAS'

FAVOURITE_SETTINGS = {
                    'INDEX': 'travelbook.views.travelbook_index',
                    'VIEW': 'travelbook.views.travelbook_view',
                    'NEW_FAVOURITE_LABEL': 'Name of new travel book',
                    'FAVOURITE_LABEL': 'Travel book',
                    'PREVIEW_DELETE_TEMPLATE': 'travelbook/travel_delete_preview.html',
                    'FORM_DELETE_TEMPLATE': 'travelbook/travel_index.html',
                   }


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
