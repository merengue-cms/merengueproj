from django.template import Library

register = Library()


@register.inclusion_tag('odtexport/images_rendering.xml')
def images_rendering(content):
    return {'content': content}
