# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from os import path

ugettext = lambda s: s  # dummy ugettext function, as said on django docs

MERENGUEDIR = path.dirname(path.abspath(__file__))

# List  of  callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    #('django.template.loaders.cached.Loader', (
        'merengue.theming.loader.load_template_source',  # for enabling theme support in Merengue
        'django.template.loaders.filesystem.load_template_source',
        'django.template.loaders.app_directories.load_template_source',
        'django.template.loaders.eggs.load_template_source',
    #)),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'merengue.context_processors.all_context',
    'merengue.theming.context_processors.media',
    'merengue.section.context_processors.section',
)

TEMPLATE_DIRS = (
    path.join(MERENGUEDIR, 'templates'),
)

# merengue exclusive installed apps. you have to use at least these apps in your INSTALLED_APPS project settings
MERENGUE_APPS = (
    'merengue.registry',
    'merengue.pluggable',
    'merengue.multimedia',
    'merengue.base',
    'merengue.section',
    'merengue.perms',
    'merengue.theming',
    'merengue.action',
    'merengue.block',
    'merengue.viewlet',
    'merengue.portal',
    'merengue.internallinks',
    'merengue.collection',
    'merengue.review',
    'merengue.uitools',
    'merengue.collab',  # Please, keep this application in last place cause it's used to know when activate plugins after migration
    'merengue.workflow',
)

HTTP_STATUS_CODE_TEMPLATES = {
    403: '403.html',
    404: '404.html',
}

# merengue usual installed apps. you can use this variable in your INSTALLED_APPS project settings
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    #'django.contrib.comments',
    'django_extensions',
    'template_utils',
    'debug_toolbar',
    'cmsutils',
    'transmeta',
    'transhette',
    'tagging',
    'sorl.thumbnail',
    'pagination',
    'inplaceeditform',
    'searchform',
    'inlinetrans',
    'mptt',
    'tinyimages',
    'rating',
    'captcha',
    'south',
    'threadedcomments',
    'autoreports',
    'formadmin',
    'johnny',
    'oot',
    'genericforeignkey',
    'oembed',
    'ajax_select',
    'notification',
    'compressor',
    'announcements',
) + MERENGUE_APPS

# merengue exclusive middlewares. you have to put at least these middleware in your project settings
MERENGUE_MIDDLEWARE_CLASSES = (
    'merengue.middleware.RemoveRandomAjaxParameter',
    'merengue.section.middleware.RequestSectionMiddleware',
    'merengue.section.middleware.DebugSectionMiddleware',
    'merengue.multimedia.middleware.MediaMiddleware',
    'merengue.middleware.SimplifiedLayoutMiddleware',
    'merengue.middleware.LocaleMiddleware',
    'merengue.middleware.HttpStatusCodeRendererMiddleware',
    'merengue.pluggable.middleware.ActivePluginsMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
)

# merengue usual middleware list. you can use this variable in your MIDDLEWARE_CLASSES project settings

PRE_MERENGUE_MIDDLEWARE_CLASSES = (
    'johnny.middleware.LocalStoreClearMiddleware',  # this has to be first
    #'cmsutils.middleware.ProfileMiddleware', # remove comment if you want to profile your website
    #'cmsutils.middleware.I18NUpdateCacheMiddleware', # removed anonymous cache middleware
    'johnny.middleware.QueryCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cmsutils.middleware.AutomatizedTestingMiddleware',
)

POST_MERENGUE_MIDDLEWARE_CLASSES = (
    #'django.middleware.gzip.GZipMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'merengue.section.middleware.ResponseSectionMiddleware',
    'merengue.pluggable.middleware.PluginMiddlewaresProxy',
    'merengue.block.middleware.RenderBlockMiddleware',
    #'cmsutils.middleware.I18NFetchFromCacheMiddleware', # this has to be last # removed anonymous cache middleware
)

MIDDLEWARE_CLASSES = PRE_MERENGUE_MIDDLEWARE_CLASSES + MERENGUE_MIDDLEWARE_CLASSES + POST_MERENGUE_MIDDLEWARE_CLASSES

# merengue status list for contents workflow.
STATUS_LIST = (
    ('draft', ugettext('Borrador')),
    ('pending', ugettext('Pendiente')),
    ('published', ugettext('Publicado')),
)
DEFAULT_STATUS = 'draft'

# max integer value (database safe)
MAX_INT_VALUE = 2147483647

# merengue default directory for plugins
PLUGINS_DIR = 'plugins'

# merengue required plugins in project (will be activated by default)
REQUIRED_PLUGINS = ('core', )

# if merengue will detect new plugins in file system
DETECT_NEW_PLUGINS = True

# if merengue will detect broken plugins
DETECT_BROKEN_PLUGINS = True

# The module to store session data
SESSION_ENGINE = 'merengue.backends.db'

# Users can manage sections they own and their related objects
ACQUIRE_SECTION_OWNERSHIP = False

# cache default settings
CACHE_MIDDLEWARE_SECONDS = 3600 * 24
CACHE_MIDDLEWARE_KEY_PREFIX = 'merengue'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'merengue'

# Google API Key for localhost:8000
# http://code.google.com/apis/maps/signup.html
GOOGLE_MAPS_API_KEY = 'ABQIAAAAddxuy_lt2uAk9Y30XD3MJhQCULP4XOMyhPd8d_NrQQEO8sT8XBRRmJjQjU4qrycwOKb_v70y1h_1GQ'
GOOGLE_MAPS_API_VERSION = '3.x'
DEFAULT_LATITUDE = 36.851362
DEFAULT_LONGITUDE = -5.753321

# Pagination options
PAGE_VARIABLE = 'page'

# Default merengue options for tinyMCE
TINYMCE_MEDIA = None  # set to something like: MEDIA_URL + "cmsutils/js/widgets/tiny_mce/"
EXTRA_MCE = {
    'theme_advanced_buttons1': 'bold,italic,copy,paste,pasteword,underline,justifyleft,justifycenter,justifyright,justifyfull,bullist,numlist,outdent,indent',
}

TINYMCE_EXTRA_MEDIA = {
   'js': [],
   'css': [],
}

# Captcha default settings
CAPTCHA_SETTINGS = {
    'NUMBER_SWAP': {
                    'O': '0',
                    'Z': '2',
                    'S': '5',
                    'B': '8',
    },
    'CASE_SENSITIVE': False,
    'USE_EXTRA_IMAGE': False,
}

# Default parameters for suggestion box
SUGGESTION_BOX_EMAIL = 'info@foo.com'
CONTACT_SUGGESTIONBOX_PREFIX = 'SUGGESTION BOX'

# For transhette
ENABLE_TRANSLATION_SUGGESTIONS = False

# Map parameters
MAP_FILTRABLE_MODELS = (
    'base.basecontent',
)

DEBUG_TOOLBAR_EXCLUDED_URLS = (
    r'^/tinyimages/',
)

# ajax_select
AJAX_LOOKUP_CHANNELS = {
    'perms_user': ('merengue.perms.lookups', 'UserLookup'),
    'perms_group': ('merengue.perms.lookups', 'GroupLookup'),
}

JQUERY_BASE_MEDIA = 'merengue/js/'

# Customization Comment app for merengue, feedback
# COMMENTS_APP = 'plugins.feedback'

MENU_PORTAL_SLUG = 'portal_menu'

# Dictionary with fixtures to load for every application
# After migrating (with south) 'foo' application Merengue will load
# every SITE_FIXTURES['foo'] files
# Syntax: {
#    'app_name': ('fixture_to_load1', 'fixture_to_load2', ...),
#    ...}
SITE_FIXTURES = {}

SERIALIZATION_MODULES = {
    "xml": "merengue.xml_serializer",
}

# Prefix for all merengue URLs
MERENGUE_URLS_PREFIX = 'cms'

# Login and logout settings
LOGIN_URL = '/%s/login/' % MERENGUE_URLS_PREFIX
LOGOUT_URL = '/%s/logout/' % MERENGUE_URLS_PREFIX
LOGIN_REDIRECT_URL = '/'

# Merengue test runner
TEST_RUNNER = 'merengue.test.run_tests'

# Merengue manage file
MANAGE_FILE = 'manage.py'

# sys.executable
# /usr/bin/python
SYS_EXECUTABLE = None

JOHNNY_TABLE_BLACKLIST = ('south_migrationhistory', 'django_content_type', 'thumbnail_kvstore')

# Path for translation catalogs search
LOCALE_PATHS = (
    path.join(MERENGUEDIR, 'locale'),
)

# Theme default preview image. The real path would be path.join(MEDIA_URL, DEFAULT_PLUGIN_PREVIEW)
DEFAULT_THEME_PREVIEW = 'merengue/img/preview_merengue.png'

STATIC_ROLES = [u'Anonymous User', u'Owner']

STATIC_WORKFLOW_DATA = {
    'workflow': [u'basic-workflow'],
    'states': [u'draft', u'pending', u'published'],
    'transitions': [u'set-as-pending', u'publish', u'set-as-draft'],
}

# inplaceeditform
ADAPTOR_INPLACEEDIT = {'textarea': 'merengue.uitools.fields.AdaptorTinyMCEField'}

# Plugin default preview image. The real path would be path.join(MEDIA_URL, DEFAULT_PLUGIN_PREVIEW)
DEFAULT_PLUGIN_PREVIEW = path.join('merengue', 'img', 'preview_merengue.png')

# Num element per page in collections
NUM_ELEM_PER_PAGE_DEFAULT = 10

# Search in genericforeingkey model admins
SEARCH_MODELADMIN = True

# Settings to autoreports
AUTOREPORTS_FUNCTIONS = True
AUTOREPORTS_INITIAL = True
AUTOREPORTS_I18N = True
AUTOREPORTS_SUBFIX = True

# Default workflow
DEFAULT_WORKFLOW = 1
