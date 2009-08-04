from django.contrib.admin.sites import AdminSite as DjangoAdminSite
from django.utils.importlib import import_module

# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False


def autodiscover(admin_site=None):
    """
    Like Django autodiscover, it search for admin.py modules and fail silently when
    not present.

    Main difference is that you can pass admin_site by parameter for registration
    in this admin site.
    """
    # Bail out if autodiscover didn't finish loading from a previous call so
    # that we avoid running autodiscover again when the URLconf is loaded by
    # the exception handler to resolve the handler500 view.  This prevents an
    # admin.py module with errors from re-registering models and raising a
    # spurious AlreadyRegistered exception (see #8245).
    global LOADING
    if LOADING:
        return
    LOADING = True

    import imp
    from django.conf import settings

    if admin_site is None:
        admin_site = site

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an admin.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for admin.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own admin registration.
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's admin.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its admin.py doesn't exist
        try:
            imp.find_module('admin', app_path)
        except ImportError:
            continue

        # Step 3: import the app's admin file. If this has errors we want them
        # to bubble up.
        mod = __import__('%s.admin' % app, {}, {}, app.split('.'))
        # Step 4: look for register function and call it, passing admin site
        # as parameter
        register_func = getattr(mod, 'register', None)
        if register_func is not None and callable(register_func):
            register_func(admin_site)

    # autodiscover was successful, reset loading flag.
    LOADING = False


class AdminSite(DjangoAdminSite):
    pass


# This global object represents the default admin site, for the common case.
# You can instantiate AdminSite in your own code to create a custom admin site.
site = AdminSite()
