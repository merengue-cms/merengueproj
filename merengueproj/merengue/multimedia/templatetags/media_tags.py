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

from django import template

from oembed.templatetags.oembed_tags import OEmbedNode


register = template.Library()


SLIDE_TYPES = ['photo', 'video', 'panoramicview', 'image3d', 'audio']


@register.inclusion_tag('media_slide.html', takes_context=True)
def media_slide(context, content):
    multimedia = content.multimedia.published().filter(class_name__in=SLIDE_TYPES).order_by('multimediarelation__order')
    return {'multimedia_list': multimedia,
            'content': content,
            'street_view': True,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


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
def multimedia_slide_link(context, multimedia, content):
    class_name = multimedia.class_name
    size = '200x150'
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
        original_render = super(ExtraOembedNode, self).render(context)
        if not self.var_name:
            return original_render
        context[self.var_name]=original_render
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
