"""
The main DebugToolbar class that loads and renders the Toolbar.
"""
from django.template.loader import render_to_string

class DebugToolbar(object):

    def __init__(self, request):
        self.request = request
        self.panels = []
        # Override this tuple by copying to settings.py as `DEBUG_TOOLBAR_PANELS`
        self.default_panels = (
            'debug_toolbar.panels.version.VersionDebugPanel',
            'debug_toolbar.panels.timer.TimerDebugPanel',
            'debug_toolbar.panels.headers.HeaderDebugPanel',
            'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
            'debug_toolbar.panels.sql.SQLDebugPanel',
            'debug_toolbar.panels.cache.CacheDebugPanel',
            'debug_toolbar.panels.template.TemplateDebugPanel',
            'debug_toolbar.panels.logger.LoggingPanel',
        )
        self.load_panels()

    def load_panels(self):
        """
        Populate debug panels
        """
        from django.conf import settings
        from django.core import exceptions

        # Check if settings has a DEBUG_TOOLBAR_PANELS, otherwise use default
        if hasattr(settings, 'DEBUG_TOOLBAR_PANELS'):
            self.default_panels = settings.DEBUG_TOOLBAR_PANELS

        for panel_path in self.default_panels:
            try:
                dot = panel_path.rindex('.')
            except ValueError:
                raise exceptions.ImproperlyConfigured, '%s isn\'t a debug panel module' % panel_path
            panel_module, panel_classname = panel_path[:dot], panel_path[dot+1:]
            try:
                mod = __import__(panel_module, {}, {}, [''])
            except ImportError, e:
                raise exceptions.ImproperlyConfigured, 'Error importing debug panel %s: "%s"' % (panel_module, e)
            try:
                panel_class = getattr(mod, panel_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured, 'Toolbar Panel module "%s" does not define a "%s" class' % (panel_module, panel_classname)

            try:
                panel_instance = panel_class()
            except:
                print panel_class
                raise # Bubble up problem loading panel

            self.panels.append(panel_instance)

    def render_toolbar(self):
        """
        Renders the overall Toolbar with panels inside.
        """
        return render_to_string('debug_toolbar/base.html', {
            'panels': self.panels,
            'BASE_URL': self.request.META.get('SCRIPT_NAME', ''),
        })
