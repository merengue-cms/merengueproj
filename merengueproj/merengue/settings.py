ugettext = lambda s: s # dummy ugettext function, as said on django docs

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

# merengue exclusive installed apps. you have to use at least these apps in your INSTALLED_APPS project settings
MERENGUE_APPS = (
    'merengue.registry',
    'merengue.multimedia',
    'merengue.places',
    'merengue.base',
    'merengue.section',
    'merengue.plugins',
    'merengue.themes',
    'merengue.action',
    'merengue.block',
    'merengue.portal',
    'merengue.internallinks',
    'merengue.collab',
)

# merengue usual installed apps. you can use this variable in your INSTALLED_APPS project settings
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.gis',
    #'django.contrib.comments',
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
    'captcha',
    'south',
) + MERENGUE_APPS

# merengue exclusive middlewares. you have to put at least these middleware in your project settings
MERENGUE_MIDDLEWARE_CLASSES = (
    'merengue.middleware.RemoveRandomAjaxParameter',
    'merengue.section.middleware.SectionMiddleware',
    'merengue.section.middleware.DebugSectionMiddleware',
    'merengue.middleware.SimplifiedLayoutMiddleware',
    'merengue.middleware.LocaleMiddleware',
    'merengue.plugins.middleware.ActivePluginsMiddleware',
)

# merengue usual middleware list. you can use this variable in your MIDDLEWARE_CLASSES project settings
MIDDLEWARE_CLASSES = (
    'cmsutils.middleware.I18NUpdateCacheMiddleware', # this has to be first
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cmsutils.middleware.AutomatizedTestingMiddleware',
) + MERENGUE_MIDDLEWARE_CLASSES + (
    #'django.middleware.gzip.GZipMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'cmsutils.middleware.I18NFetchFromCacheMiddleware', # this has to be last
)

# merengue status list for contents workflow.
STATUS_LIST = (
    ('draft', ugettext('Borrador')),
    ('pending', ugettext('Pendiente')),
    ('published', ugettext('Publicado')),
    ('passive', ugettext('Registro pasivo')),
    ('deleted_in_plone', ugettext('Borrado en Plone')),
)

# merengue default directory for plugins
PLUGINS_DIR = 'plugins'

ACTIVED_DEFAULTS_PLUGINS = ('core', )

# cache default settings
CACHE_BACKEND = 'locmem:///'
CACHE_MIDDLEWARE_SECONDS = 3600*24
CACHE_MIDDLEWARE_KEY_PREFIX = 'merengue'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# Google API Key for localhost:8000
# http://code.google.com/apis/maps/signup.html
GOOGLE_MAPS_API_KEY = 'ABQIAAAAddxuy_lt2uAk9Y30XD3MJhQCULP4XOMyhPd8d_NrQQEO8sT8XBRRmJjQjU4qrycwOKb_v70y1h_1GQ'
GOOGLE_MAPS_API_VERSION = '3.x'
DEFAULT_LATITUDE = 36.851362
DEFAULT_LONGITUDE = -5.753321

# Pagination options
PAGE_VARIABLE = 'page'

# Default merengue options for tinyMCE
TINYMCE_MEDIA = None # set to something like: MEDIA_URL + "cmsutils/js/widgets/tiny_mce/"
EXTRA_MCE = {
    'theme_advanced_buttons1': 'bold,italic,copy,paste,pasteword,underline,justifyleft,justifycenter,justifyright,justifyfull,bullist,numlist,outdent,indent',
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
}

# Default parameters for suggestion box
SUGGESTION_BOX_EMAIL = 'info@foo.com'
CONTACT_SUGGESTIONBOX_PREFIX = 'SUGGESTION BOX'


# Map parameters
MAP_FILTRABLE_MODELS = (
    'base.basecontent',
)

# Customization Comment app for merengue, feedback
# COMMENTS_APP = 'plugins.feedback'
