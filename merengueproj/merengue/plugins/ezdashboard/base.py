from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.importlib import import_module


class Gadget(object):
    """
    Abstract base class for gadgets
    """
    name = 'abstract-base-gadget'
    version = 0.1
    description = 'abstract base gadget'
    meta_template = 'ezgadgets/meta.xml'
    content_template = None # to override in subclasses
    events = ()
    slots = ()

    def __init__(self, request):
        self.request = request

    def __unicode__(self):
        return self.name

    def _site_url(self):
        site = Site.objects.get_current()
        return '%s://%s' % ((self.request.is_secure() and "https" or "http"),
                            site.domain)

    def _build_context(self):
        site = Site.objects.get_current()
        # We use import_module to avoid circular dependencies
        plugin_mod = import_module("plugins.ezdashboard.config").PluginConfig
        plugin_config = plugin_mod.get_config()
        return {
            'gadget': self,
            'SITE_DOMAIN': site.domain,
            'SITE_URL': self._site_url(),
            'EZWEB_URL': plugin_config['url'].value,
        }

    def meta_url(self):
        return '%s%s' % (self._site_url(),
                         reverse('plugins.ezdashboard.views.gadget_meta',
                         args=[self.name]))

    def url(self):
        return '%s%s' % (self._site_url(),
                         reverse('plugins.ezdashboard.views.gadget_view',
                         args=[self.name]))

    def meta(self):
        return render_to_string(self.meta_template, self._build_context(),
                                context_instance=RequestContext(self.request))

    def render_content(self, extra_context=None):
        context = self._build_context()
        if extra_context is not None:
            context.update(extra_context)
        return render_to_string(self.content_template, context,
                                context_instance=RequestContext(self.request))

    def content(self):
        message = u'%s gadget must override content method' % self
        raise NotImplementedError(message)
