from django.template import Library

register = Library()


@register.inclusion_tag('odtexport/images_rendering.xml')
def images_rendering(content):
    return {'content': content}


@register.inclusion_tag('odtexport/render_gmap.xml')
def render_gmap(content, height=500, weight=300, zoom=15):
    base_url = 'http://maps.google.com/maps/api/staticmap'
    coords = content.location.main_location.coords
    args = 'center=%s,%s&markers=%s,%s' % ((coords[1], coords[0]) * 2)
    args += '&zoom=%s&size=%sx%s&sensor=true' % (zoom, height, weight)

    return {'gmap_url': '%s?%s' % (base_url, args)}
