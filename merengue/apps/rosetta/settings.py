import os
from django.conf import settings

# Number of messages to display per page.
MESSAGES_PER_PAGE = 10


# Enable Google translation suggestions
ENABLE_TRANSLATION_SUGGESTIONS = True

# Search into entry occurrences
SEARCH_INTO_OCCURRENCES = False

"""
When running WSGI daemon mode, using mod_wsgi 2.0c5 or later, this setting
controls whether the contents of the gettext catalog files should be
automatically reloaded by the WSGI processes each time they are modified.

Notes:

 * The WSGI daemon process must have write permissions on the WSGI script file
   (as defined by the WSGIScriptAlias directive.)
 * WSGIScriptReloading must be set to On (it is by default)
 * For performance reasons, this setting should be disabled in production environments
 * When a common rosetta installation is shared among different Django projects,
   each one running in its own distinct WSGI virtual host, you can activate
   auto-reloading in individual projects by enabling this setting in the project's
   own configuration file, i.e. in the project's settings.py

Refs:

 * http://code.google.com/p/modwsgi/wiki/ReloadingSourceCode
 * http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIReloadMechanism

"""
WSGI_AUTO_RELOAD = False


"""
    Options:
    * "test" for a django instance (this do a touch over settings.py for reload)
    * "apache2"
    * "httpd"
    * "wsgi"
    * "restart_script <script_path_name>"

"""
AUTO_RELOAD_METHOD = 'test'

SHOW_NATIVE_LANGUAGE = True

FORCE_NATIVE_LANGUAGE_TO = 'es'

MAKEMESSAGES_OPTIONS = {'all': True,
            'domain': 'django',
            'extensions': None,
            'locale': None,
            'pythonpath': None,
            'settings': None,
            'traceback': None,
            'verbosity': '1',
            'locale-path': os.path.join(settings.BASEDIR, 'locale'),
            }

MAKEMESSAGES_COMMAND = "inline_makemessages"

TRANSLATORS_GROUPS = ('translators', 'editores', 'traductores')
