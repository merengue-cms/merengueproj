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

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string


class Gadget(object):
    """
    Abstract base class for gadgets
    """
    name = 'abstract-base-gadget'
    version = 0.1
    description = 'abstract base gadget'
    meta_template = 'ezgadgets/meta.xml'
    content_template = None  # to override in subclasses
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
        # We use import get_plugin here to avoid circular dependencies
        from merengue.pluggable.utils import get_plugin
        plugin_config = get_plugin('ezdashboard').get_config()
        return {
            'gadget': self,
            'SITE_DOMAIN': site.domain,
            'SITE_URL': self._site_url(),
            'EZWEB_URL': plugin_config['url'].value,
        }

    @property
    def image_url(self):
        return '%s%sgadgets/%s.jpg' % (self._site_url(), settings.MEDIA_URL, self.name)

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
