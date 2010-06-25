# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

# -*- encoding: utf-8 -*-
# Django settings for merengue project.

from os import path
from merengue.settings import *

ugettext = lambda s: s # dummy ugettext function, as said on django docs

BASEDIR = path.dirname(path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = DEBUG

ADMINS = (
    ('Your Name', 'youremail@yourdomain.org'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
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
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', ugettext('English')),
    ('es', ugettext('Español')),
    ('fr', ugettext('Français')),
)

SITE_ID = 1
SITE_REGISTER_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# PostGIS extension flag
USE_GIS = False

if USE_GIS:
    INSTALLED_APPS += ('django.contrib.gis', 'merengue.places', )
    if DATABASE_ENGINE == 'postgresql_psycopg2':
        TEST_DB_CREATION_SUFFIX = 'WITH TEMPLATE template_postgis'

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

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    # put here aditional middlewares
)

ROOT_URLCONF = '{{ project_name }}.urls'

TEMPLATE_DIRS = (
    path.join(BASEDIR, 'templates'),
) + TEMPLATE_DIRS

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'

INSTALLED_APPS += (
    # put here your project django apps
)

SVNDIR = path.join(BASEDIR, 'apps')

TEST_DB_CREATION_SUFFIX = 'WITH TEMPLATE template_postgis'

FIXTURE_DIRS = (
    path.join(BASEDIR, 'fixtures', ),
)

SITE_FIXTURES = {
    # Site fixtures that will be loaded after data migration. Syntax:
    # 'app_name': ('fixture1', 'fixture2', ...)
}

BUILDBOT_IP = '192.168.11.209'
INTERNAL_IPS = ('127.0.0.1', '80.36.82.38', BUILDBOT_IP)

# Pagination options
LIMIT_URL_SPIDER_TEST = 20

# Overwrite options tinyMCE
TINYMCE_MEDIA = MEDIA_URL + "cmsutils/js/widgets/tiny_mce/"

TINYMCE_EXTRA_MEDIA = {
   'js': [],
   'css': [],
}

SEARCHBAR_MIN_RESULTS = 5

LOGOUT_PROTECTED_URL_REDIRECTS = (
    #(r'^/regularexpresion/(.*)$', '/redirect_url'),
)

PRODUCTION_DB_URL = ""
PRODUCTION_DB_UPDATE_PASSWORDS = (('admin', 'admin'), )

# For transhette
ENABLE_TRANSLATION_SUGGESTIONS = False

# For johnny cache. Johnny cache key prefix should not be the same in other projects
CACHE_BACKEND = 'johnny.backends.locmem:///'
JOHNNY_MIDDLEWARE_KEY_PREFIX = '%s-cache' % DATABASE_NAME

# Allow overwriting any configuration in optional settings_local.py
# (it can be used to set up your own database, debug and cache options, contact mails...)
try:
    from settings_local import *
except ImportError:
    pass
