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

import hashlib
from time import time

from django.conf import settings
from django.core import signals
from django.core.cache import cache
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.http import urlquote
from django.utils.log import getLogger
from django.utils.translation import get_language, ugettext as _

from merengue.block.models import RegisteredBlock
from merengue.registry import params
from merengue.registry.items import RegistrableItem
from merengue.registry.signals import item_registered


logger = getLogger('merengue.block')

# block information for debugging purposes
block_debug_info = {}


class BaseBlock(RegistrableItem):
    model = RegisteredBlock
    singleton = False
    is_addable = True
    cache_allowed = True
    default_caching_params = {
       'enabled': False,
       'only_anonymous': False,
       'timeout': 0,
       'vary_on_url': False,
       'vary_on_language': True,
       'vary_on_user': False,
    }

    config_params = [
        params.Single(name='css_class', label=_('css class to add to this block'), default=''),
        ]

    def __init__(self, reg_item):
        super(BaseBlock, self).__init__(reg_item)
        self.content = getattr(reg_item, 'content', None)

    @classmethod
    def get_category(cls):
        return 'block'

    def get_rendered_content(self, request, render_args):
        """ render the block content, using cached content is needed """
        #import ipdb; ipdb.set_trace()
        if settings.DEBUG:
            start = time()
        rendered_content = self.get_cached_content(request)
        if rendered_content is None:
            is_cached = False
            rendered_content = self.render(*render_args)
            self.set_cached_content(rendered_content, request)
        else:
            is_cached = True
        if settings.DEBUG:
            block_debug_info
            stop = time()
            duration = stop - start
            block_id = '%s.%s:%d' % (self.get_module(), self.get_class_name(), self.reg_item.id)
            block_debug_info[block_id] = {
                'block': block_id,
                'module': self.get_module(),
                'class_name': self.get_class_name(),
                'is_cached': is_cached,
                'time': duration,
            }
            logger.debug('(%.3f) %s; cached=%s' % (duration, block_id, is_cached),
                extra={'duration': duration, 'block': block_id, 'is_cached': is_cached}
            )
        return rendered_content

    def render_block(self, request, template_name='block.html', block_title=None,
                     context=None):
        if context is None:
            context = {}
        registered_block = self.get_registered_item()
        css_class = self.get_config().get('css_class', None)
        css_class = css_class and css_class.get_value() or ''
        block_context = {
            'block_name': registered_block.name,
            'placed_at': registered_block.placed_at,
            'fixed_place': getattr(registered_block, 'fixed_place', False),
            'block_title': block_title or registered_block.name,
            'block': registered_block,
            'css_class': css_class,
            'has_config': self.has_config(),
        }
        block_context.update(context)
        rendered_content = render_to_string(template_name, block_context,
                                            context_instance=RequestContext(request))
        return rendered_content

    def _get_cache_key(self, request):
        registered_block = self.reg_item
        key_prefix = 'blocks_cache_%d' % registered_block.id
        if registered_block.cache_vary_on_url:
            key_prefix += '-%s' % urlquote(request.META['PATH_INFO'])
            params = request.GET.urlencode()
            if params:
                key_prefix += '?%s' % params
        if registered_block.cache_vary_on_language:
            key_prefix += '-%s' % get_language()
        if registered_block.cache_vary_on_user:
            key_prefix += '-%s' % request.user.username
        if len(key_prefix) > settings.CACHE_MAX_KEY:
            key_prefix = hashlib.md5(key_prefix).hexdigest()
        return key_prefix

    def _get_registry_cache_key(self):
        return 'blocks_cache_registry'

    def is_cacheable(self, request):
        registered_block = self.reg_item
        return registered_block.is_cached and \
               not (not request.user.is_anonymous() and registered_block.cache_only_anonymous)

    def get_cached_content(self, request):
        if not self.is_cacheable(request):
            return None
        cache_key = self._get_cache_key(request)
        return cache.get(cache_key)

    def set_cached_content(self, content, request):
        if not self.is_cacheable(request):
            return  # not need to cache nothing
        cache_key = self._get_cache_key(request)
        self._register_cache_key(cache_key)
        content = '<div class="cached-block">%s</div>' % content
        return cache.set(cache_key, content, self.reg_item.cache_timeout)

    def set_default_caching(self):
        reg_block = self.reg_item
        def_caching_params = self.default_caching_params
        reg_block.is_cached = def_caching_params.get('enabled', False)
        reg_block.cache_timeout = def_caching_params.get('timeout', 0)
        reg_block.cache_only_anonymous = def_caching_params.get('only_anonymous', False)
        reg_block.cache_vary_on_language = def_caching_params.get('vary_on_language', True)
        reg_block.cache_vary_on_url = def_caching_params.get('vary_on_url', False)
        reg_block.cache_vary_on_user = def_caching_params.get('vary_on_user', False)
        reg_block.save

    def invalidate_cache(self):
        registry_cache_key = self._get_registry_cache_key()
        cache_registry = self._get_registry_cache()
        registered_block = self.reg_item
        cache.delete_many(cache_registry[registered_block.id])
        del cache_registry[registered_block.id]
        cache.set(registry_cache_key, cache_registry)

    def _get_registry_cache(self):
        registry_cache_key = self._get_registry_cache_key()
        registered_block = self.reg_item
        cache_registry = cache.get(registry_cache_key)
        if cache_registry is None:
            cache_registry = {}
        if registered_block.id not in cache_registry:
            cache_registry[registered_block.id] = []
        return cache_registry

    def _register_cache_key(self, cache_key):
        registry_cache_key = self._get_registry_cache_key()
        cache_registry = self._get_registry_cache()
        cache_registry[self.reg_item.id].append(cache_key)
        cache.set(registry_cache_key, cache_registry)


class Block(BaseBlock):
    default_place = 'leftsidebar'

    def render(self, request, place, context,
               *args, **kwargs):
        raise NotImplementedError()


class ContentBlock(BaseBlock):
    default_place = 'content'

    def render(self, request, place, content, context,
               *args, **kwargs):
        raise NotImplementedError()


class SectionBlock(BaseBlock):
    default_place = 'leftsidebar'

    def render(self, request, place, section, context,
               *args, **kwargs):
        raise NotImplementedError()


def registered_block(sender, **kwargs):
    if issubclass(sender, BaseBlock):
        registered_item = kwargs['registered_item']
        registered_item.placed_at = sender.default_place
        registered_item.name = sender.name

        # optional block settings
        if hasattr(sender, 'is_fixed'):
            registered_item.is_fixed = sender.is_fixed
        if hasattr(sender, 'fixed_place'):
            registered_item.fixed_place = sender.fixed_place

        registered_item.save()


item_registered.connect(registered_block)


def reset_block_debug_info(**kwargs):
    """ Resets the block information (for debug) when a Django request is started."""
    global block_debug_info
    block_debug_info = {}
signals.request_started.connect(reset_block_debug_info)
