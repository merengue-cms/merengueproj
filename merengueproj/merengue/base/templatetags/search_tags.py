from django import template

register = template.Library()


@register.inclusion_tag('base/search_results.html', takes_context=True)
def search_results(context, result_list, with_rating=False):
    return {'result_list': result_list,
            'request': context.get('request', None),
            'MEDIA_URL': context.get('MEDIA_URL', '/media/'),
            'LANGUAGE_CODE': context.get('LANGUAGE_CODE', 'es'),
            'GOOGLE_MAPS_API_KEY': context.get('GOOGLE_MAPS_API_KEY', ''),
            'user': context['user'],
            'with_rating': with_rating,
            }
