from django.http import HttpResponse

from merengue.seo.utils import generate_sitemap


def sitemap(request, with_portal_links=True, with_menu_portal=True,
                     with_sections=True, with_menu_section=False,
                     with_contents=False):
    sitemap = generate_sitemap(with_portal_links=with_portal_links,
                               with_menu_portal=with_menu_portal,
                               with_sections=with_sections,
                               with_menu_section=with_menu_section,
                               with_contents=with_contents)
    return HttpResponse(sitemap, mimetype="text/xml")
