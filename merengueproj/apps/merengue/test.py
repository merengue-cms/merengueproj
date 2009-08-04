from django.conf import settings
from django.test.simple import run_tests as django_run_tests


def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    from django.db import connection
    old_table_creation_suffix = connection.creation.sql_table_creation_suffix

    def new_table_creation_suffix():
        suffix = old_table_creation_suffix()
        return suffix + ' ' + settings.TEST_DB_CREATION_SUFFIX
    connection.creation.sql_table_creation_suffix = new_table_creation_suffix

    old_middlewares = settings.MIDDLEWARE_CLASSES
    new_middlewares = list(old_middlewares)
    new_middlewares.remove('cmsutils.middleware.I18NUpdateCacheMiddleware')
    new_middlewares.remove('cmsutils.middleware.I18NFetchFromCacheMiddleware')
    settings.MIDDLEWARE_CLASSES = tuple(new_middlewares)

    result = django_run_tests(test_labels, verbosity, interactive, extra_tests)

    connection.creation.sql_table_creation_suffix = old_table_creation_suffix
    settings.MIDDLEWARE_CLASSES = old_middlewares

    return result
