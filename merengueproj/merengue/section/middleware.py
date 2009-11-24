from django.conf import settings
from django.core.cache import cache
from django.http import Http404


class RequestSectionMiddleware(object):
    """This middleware autodiscovers the current section from the url"""

    def process_request(self, request):
        from merengue.section.models import BaseSection

        section = None
        if request.path:
            path_list = request.path.split('/')
            if path_list[1] == 'sections':
                section_position = 2
            else:
                section_position = 1
            section_path = path_list[section_position]
            slugs_cache_key = 'published_section_slugs'
            published_slugs = cache.get(slugs_cache_key)
            if published_slugs is None:
                published_slugs = [v[0] for v in BaseSection.objects.published().values_list('slug')]
                cache.set(slugs_cache_key, published_slugs)
            if section_path in published_slugs:
                try:
                    cache_key = 'app_section_%s' % section_path
                    section = cache.get(cache_key)
                    if section is None:
                        section = BaseSection.objects.get(slug=section_path)
                        cache.set(cache_key, section)
                except:
                    # we put an blank except because some times in WSGI in a heavy loaded environments
                    # backends specific exceptions can be thrown, i.e. psycopg.ProgrammingError
                    pass
        request.section = section


class ResponseSectionMiddleware(object):
    """This middleware autodiscovers the current section from the url"""

    def process_response(self, request, response):
        from merengue.section.views import section_dispatcher
        if response.status_code != 404:
            return response # No need to check for a section for non-404 responses.
        try:
            return section_dispatcher(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except:
            if settings.DEBUG:
                raise
            return response


class DebugSectionMiddleware(object):
    """This middleware checks for a GET parameter for a special debug mode"""

    def process_request(self, request):
        use_section_data = request.GET.get('use_section_data', False)
        if use_section_data:
            request.use_section_data = True
