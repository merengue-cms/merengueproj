import operator

from django import template
from django.utils.text import unescape_entities


register = template.Library()


@register.inclusion_tag('base/content_title.html', takes_context=True)
def content_title(context, content):
    return {'content': content, 'request': context.get('request')}


@register.inclusion_tag('base/content_admin_action.html', takes_context=True)
def content_admin_action(context, content):
    user = context.get('request').user
    if hasattr(content, 'can_edit') and callable(content.can_edit):
        can_edit = content.can_edit(user)
    else:
        can_edit = user.is_superuser or user.has_perm(
            content._meta.app_label + '.' + content._meta.get_change_permission())
    return {
        'content': content,
        'user': user,
        'can_edit': can_edit,
        'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
        'THEME_URL': context.get('THEME_URL'),
    }


@register.inclusion_tag('base/content_specialized_fields.html', takes_context=True)
def content_specialized_fields(context, content):
    specialized_fields = []
    if content.__class__.__subclasses__():
        # if content is not a leaf content we get real content
        instance = content._get_real_instance()
    else:
        instance = content

    return {'content': content, 'user': context.get('request').user,
            'specialized_fields': specialized_fields}


@register.inclusion_tag('base/content_handicapped_services.html', takes_context=True)
def content_handicapped_services(context, content):
    return {'content': content, 'request': context.get('request')}


@register.inclusion_tag('base/content_features.html', takes_context=True)
def content_features(context, content):
    return {'content': content, 'request': context.get('request')}


@register.inclusion_tag('base/address_info.html', takes_context=True)
def address_info(context, content, showtitle=True):
    return {'content': content,
            'showtitle': showtitle,
            'request': context.get('request')}


@register.inclusion_tag('base/address_info_provinces_separated.html', takes_context=True)
def address_info_provinces_separated(context, content):
    return {'content': content, 'request': context.get('request')}


@register.inclusion_tag('base/content_cities.html', takes_context=True)
def content_cities(context, content):
    return {'content': content, 'request': context.get('request')}


@register.inclusion_tag('base/content_provinces.html', takes_context=True)
def content_provinces(context, content):
    return {'content': content, 'request': context.get('request')}


@register.inclusion_tag('base/content_provinces_cities.html', takes_context=True)
def content_provinces_cities(context, content):
    provinces_cities = {}
    provinces = {}
    if content.location:
        for basecity in content.location.cities.all().select_related('province'):
            province = basecity.province
            provinces[province.id] = province
            cities = provinces_cities.setdefault(province.id, [])
            cities.append(basecity)

    sorted_provinces = sorted(provinces.values(), key=operator.attrgetter('name'))
    provinces_cities = [(prov, provinces_cities[prov.id]) for prov in sorted_provinces]

    return {'content': content,
            'provinces_cities': provinces_cities,
            'request': context.get('request')}


@register.inclusion_tag('base/content_villages.html', takes_context=True)
def content_villages(context, content):
    return {'content': content, 'request': context.get('request')}


@register.inclusion_tag('base/contact_info.html', takes_context=True)
def contact_info(context, content, showtitle=True):
    return contact_info_specified(context, content, None, showtitle)


@register.inclusion_tag('base/contact_info.html', takes_context=True)
def contact_info_specified(context, content, contact_info, showtitle=True):
    return {'content': content,
            'contact_info': contact_info or content.contact_info,
            'showtitle': showtitle,
            'request': context.get('request')}


@register.inclusion_tag('base/content_list.html', takes_context=True)
def content_list(context, resource_list, with_rating=False):
    return {'resource_list': resource_list,
            'request': context.get('request', None),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
            'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
            'with_rating': with_rating,
            'user': context.get('user', None),
             }


@register.inclusion_tag('places/show_cities.html', takes_context=True)
def content_related_cities(context, cities_list, with_rating=False):
    return {'resource_list': cities_list,
            'request': context.get('request', None),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
            'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
            'user': context.get('user', None),
             }


@register.inclusion_tag('base/content_related_sections.html', takes_context=True)
def content_related_sections(context, section_list, with_rating=False):
    return {'section_list': section_list,
            'request': context.get('request', None),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
            'user': context.get('user', None),
             }


@register.inclusion_tag('base/content_thumbnail.html', takes_context=True)
def content_thumbnail(context, content, no_link=False):
    return {'content': content,
            'request': context.get('request', None),
            'no_link': no_link,
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


@register.inclusion_tag('base/touristservice_thumbnail.html', takes_context=True)
def touristservice_thumbnail(context, content):
    return {'content': content,
            'request': context.get('request', None),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


@register.inclusion_tag('base/content_related_items.html', takes_context=True)
def content_related_items(context, content):
    related_items_excluded = ['story']
    related_items = content.related_items.published().exclude(class_name__in=related_items_excluded)
    related_stories = content.related_items.published().filter(class_name='story')
    related_cities = content.related_cities.all()
    related_sections = content.basesection_set.all()

    return {'content': content,
            'related_items': related_items,
            'related_stories': related_stories,
            'related_cities': related_cities,
            'related_sections': related_sections,
            'request': context.get('request', None),
            'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'), }


@register.inclusion_tag('base/photo_slide.html', takes_context=True)
def photo_slide(context, contents, slide_id='photo_slide', visible=6, parent_content=None):
    return {'contents': contents,
            'visible': visible,
            'slide_id': slide_id,
            'parent_content': parent_content,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
           }


@register.inclusion_tag('base/video_slide.html', takes_context=True)
def video_slide(context, contents, parent_content=None):
    return {'contents': contents,
            'parent_content': parent_content,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
           }


@register.inclusion_tag('base/image3d_slide.html', takes_context=True)
def image3d_slide(context, contents, parent_content=None):
    return {'contents': contents,
            'parent_content': parent_content,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
           }


@register.inclusion_tag('base/panoramic_slide.html', takes_context=True)
def panoramic_slide(context, contents, size='100x100', parent_content=None):
    return {'contents': contents,
            'parent_content': parent_content,
            'size': size,
            'MEDIA_URL': context['MEDIA_URL'],
            'request': context['request'],
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
           }


class CuttedNode(template.Node):

    def __init__(self, length, content_node):
        self.content_node = content_node
        self.length = length

    def render(self, context):
        length = self.length
        full_value = self.content_node.render(context)
        value = unescape_entities(full_value)
        if len(value) > length - 3:
            value = value[:length-3] + '...'
        return '<span title="%s">%s</span>' % (full_value, value)


def cutrender(parser, token):
    bits = list(token.split_contents())
    if len(bits) == 1:
        length = 53
    elif len(bits) != 2:
        raise template.TemplateSyntaxError, '%r takes one argument' % bits[0]
    else:
        length = int(bits[1])
    end_tag = 'end' + bits[0]
    node_content = parser.parse((end_tag, ))
    token = parser.next_token()
    return CuttedNode(length, node_content)
cutrender = register.tag(cutrender)


@register.inclusion_tag('base/cut_objects_list.html', takes_context=True)
def cut_objects_list(context, items, max_len=90, separator=', '):
    cad = ''
    count = 0
    too_long = False
    for item in items:
        if len(cad + item.name) < max_len:
            cad += item.name + separator
            count +=1
        else:
            too_long = True
            break

    return {
        'items': items[:count],
        'too_long': too_long,
    }


@register.filter
def verbose_base_content_name(value, arg=None):
    return value._get_real_instance()._meta.verbose_name


@register.filter
def real_instance(value, arg=None):
    return value._get_real_instance()


class IfNode(template.Node):

    def __init__(self, if_node, else_node):
        self.if_node = if_node
        self.else_node = else_node

    def __repr__(self):
        return '<IfNode>'

    def check(self, context):
        raise NotImplementedError

    def render(self, context):
        if self.check(context):
            return self.if_node.render(context)
        else:
            return self.else_node.render(context)


class HasFeature(IfNode):

    def __init__(self, content, feature, *args):
        self.feature = feature
        self.content = content
        super(HasFeature, self).__init__(*args)

    def check(self, context):
        content = template.Variable(self.content).resolve(context)
        feature = template.Variable(self.feature).resolve(context)
        if not hasattr(content, 'features'):
            return False
        return bool(content.features.filter(slug=feature))


def ifhasfeature(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 3:
        raise template.TemplateSyntaxError, '%r takes two arguments' % bits[0]
    content = bits[1]
    feature = bits[2]
    end_tag = 'end' + bits[0]
    node_hasfeature = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        node_nothasfeature = parser.parse((end_tag, ))
        parser.delete_first_token()
    else:
        node_nothasfeature = template.NodeList()
    return HasFeature(content, feature, node_hasfeature, node_nothasfeature)
ifhasfeature = register.tag(ifhasfeature)
