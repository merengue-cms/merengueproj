from django.http import HttpResponse

from merengue.seo.utils import generate_sitemap, true_by_default, false_by_default


def sitemap(request, with_portal_links, with_menu_portal,
                     with_sections, with_menu_section, with_contents):
    params = {}
    params['with_portal_links'] = true_by_default(with_portal_links)
    params['with_menu_portal'] = true_by_default(with_menu_portal)
    params['with_sections'] = true_by_default(with_sections)
    params['with_menu_section'] = false_by_default(with_menu_section)
    params['with_contents'] = false_by_default(with_contents)
    sitemap = generate_sitemap(**params)
    return HttpResponse(sitemap, mimetype="text/xml")
