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

import time
from urllib2 import URLError

from django import template
from django.core.cache import cache

from classytags.arguments import Argument
from classytags.core import Tag, Options
from classytags.parser import Parser
from compressor import CssCompressor, JsCompressor
from compressor.conf.settings import COMPRESS
from oembed.templatetags.oembed_tags import OEmbedNode

register = template.Library()


SLIDE_TYPES = ['photo', 'video', 'panoramicview', 'image3d', 'audio']
MINT_DELAY = 30  # on how long any compression should take to be generated
REBUILD_TIMEOUT = 2592000  # rebuilds the cache every 30 days if nothing has changed


@register.inclusion_tag('media_slide.html', takes_context=True)
def media_slide(context, content):
    return {'multimedia_list': _get_multimedia_slide_of_content(content),
            'content': content,
            'street_view': True,
            'MEDIA_URL': context['MEDIA_URL'],
            'THEME_MEDIA_URL': context.get('THEME_MEDIA_URL', context.get('MEDIA_URL', '')),
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


def _get_multimedia_slide_of_content(content):
    return content.multimedia.published().filter(class_name__in=SLIDE_TYPES).order_by('multimediarelation__order')


@register.inclusion_tag('media_files.html', takes_context=True)
def media_files(context, content):
    if not content:
        # we cannot show any media slide
        return {}
    content_files = content.multimedia.files().published().order_by('multimediarelation__order')
    return {'content': content,
            'content_files': content_files,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


@register.inclusion_tag('multimedia/slide/multimedia_slide_link.html', takes_context=True)
def multimedia_slide_link(context, multimedia, content, size=None):
    size = size or '200x150'
    class_name = multimedia.class_name
    default = multimedia.get_default_preview()
    inc_template = template.loader.select_template(['multimedia/slide/%s_slide_link.html' % class_name,
                                                    'multimedia/slide/basemultimedia_slide_link.html']).name
    request = context.get('request', None)
    if request:
        user = request.user
    else:
        user = None
    return {'multimedia': multimedia,
            'inc_template': inc_template,
            'content': content,
            'request': context.get('request', None),
            'size': size,
            'default': default,
            'user': user,
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'THEME_MEDIA_URL': context.get('THEME_MEDIA_URL', context.get('MEDIA_URL', '')),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


class ExtraOembedNode(OEmbedNode):

    def __init__(self, nodelist, width, height, var_name, size_var=None):
        self.var_name = var_name
        self.size_var = size_var
        super(ExtraOembedNode, self).__init__(nodelist, width, height)

    def render(self, context):
        if self.size_var:
            import re

            size = template.Variable(self.size_var).resolve(context)
            if size and re.match('^\d+x\d+$', size):
                self.width, self.height = size.lower().split('x')
        try:
            original_render = super(ExtraOembedNode, self).render(context)
        except URLError:
            return ''
        if not self.var_name:
            return original_render
        context[self.var_name] = original_render
        return ''


@register.tag
def extra_oembed(parser, token):
    import re

    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        tag_name = token.contents
        arg = ''
    m = re.search(r'((?P<size>[\d]+x[\d]+)|(?P<size_var>[\w_\.]+))?( as (?P<var_name>[\w_-]+))?', arg)
    if not m:
        raise template.TemplateSyntaxError, "%r tag: Invalid parameters" % tag_name
    size = m.group('size')
    if size:
        width, height = size.lower().split('x')
        if not width and height:
            raise template.TemplateSyntaxError("Oembed's optional WIDTHxHEIGH" \
                "T argument requires WIDTH and HEIGHT to be positive integers.")
    else:
        width, height = None, None
    nodelist = parser.parse(('endoembed', ))
    parser.delete_first_token()
    return ExtraOembedNode(nodelist, width, height, m.group('var_name'), m.group('size_var'))


class MediaParser(Parser):

    def parse_blocks(self):
        super(MediaParser, self).parse_blocks()
        self.blocks['nodelist'] = self.parser.parse()


class RenderBundledMedia(Tag):
    name = 'render_bundled_media'

    options = Options(
        Argument('name'),
        parser_class=MediaParser,
    )

    def cache_get(self, key):
        packed_val = cache.get(key)
        if packed_val is None:
            return None
        val, refresh_time, refreshed = packed_val
        if (time.time() > refresh_time) and not refreshed:
            # Store the stale value while the cache
            # revalidates for another MINT_DELAY seconds.
            self.cache_set(key, val, timeout=MINT_DELAY, refreshed=True)
            return None
        return val

    def cache_set(self, key, val, timeout=REBUILD_TIMEOUT, refreshed=False):
        refresh_time = timeout + time.time()
        real_timeout = timeout + MINT_DELAY
        packed_val = (val, refresh_time, refreshed)
        return cache.set(key, packed_val, real_timeout)

    @property
    def nodelist(self):
        return self.blocks['nodelist']

    def render_tag(self, context, name, nodelist):
        request = context['request']
        rendered_contents = nodelist.render(context)
        content = request.media_holder[name].render()
        if COMPRESS:
            if name == 'css':
                compressor = CssCompressor(content)
            elif name == 'js':
                compressor = JsCompressor(content)
            output = self.cache_get(compressor.cachekey)
            if output is None:
                try:
                    output = compressor.output()
                    self.cache_set(compressor.cachekey, output)
                except:
                    from traceback import format_exc
                    raise Exception(format_exc())
        else:
            output = content  # no compression
        return '%s\n%s' % (output, rendered_contents)

register.tag(RenderBundledMedia)


class AddMediaParser(Parser):

    def parse_blocks(self):
        name = self.kwargs['name'].var.token
        self.blocks['nodelist'] = self.parser.parse(
            ('endaddmedia', 'endaddmedia %s' % name)
        )
        self.parser.delete_first_token()


class AddMedia(Tag):
    name = 'addmedia'
    options = Options(
        Argument('name'),
        parser_class=AddMediaParser,
    )

    def render_tag(self, context, name, nodelist):
        request = context['request']
        rendered_contents = nodelist.render(context)
        request.media_holder[name].append(rendered_contents)
        return ""

register.tag(AddMedia)
