from django.conf import settings
from django.core.cache import cache
from django.http import Http404

from section.models import AppSection
from section.views import section_dispatcher


class SectionMiddleware(object):
    """This middleware autodiscovers the current section from the url"""

    def process_request(self, request):
        section = None
        if request.path:
            first_path_element = request.path.split('/')[1]
            if first_path_element in settings.SECTION_MAP:
                try:
                    cache_key = 'app_section_%s' % first_path_element
                    section = cache.get(cache_key)
                    if section is None:
                        section = AppSection.objects.get(slug=first_path_element)
                        cache.set(cache_key, section)
                except:
                    # we put an blank except because some times in WSGI in a heavy loaded environments
                    # backends specific exceptions can be thrown, i.e. psycopg.ProgrammingError
                    pass
        request.section = section

    def process_response(self, request, response):
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
