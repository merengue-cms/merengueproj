from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from merengue.portal.models import PortalLink
from merengue.section.models import Menu, BaseSection
from merengue.base.models import BaseContent


PRIORITY_CHOICES = {'low': 0.3,
                    'medium': 0.7,
                    'high': 1}


def _treatment_url(domain, url):
    if url and url.startswith('/'):
        return "%s%s" % (domain, url)
    return url


def generate_sitemap(with_portal_links=True, with_menu_portal=True,
                     with_sections=True, with_menu_section=True,
                     with_contents=True, priority_choices=None):
    priority_choices = priority_choices or PRIORITY_CHOICES
    domain = 'http://%s' % Site.objects.get_current().domain

    results = []
    if with_portal_links:
        for portal in PortalLink.objects.all():
            url = _treatment_url(domain, portal.get_absolute_url())
            if not url:
                continue
            results.append({'url': url,
                            'modified_date': None,
                            'priority': PRIORITY_CHOICES['high']})
    if with_menu_portal:
        menu_portal = Menu.objects.get(slug=settings.MENU_PORTAL_SLUG)
        for menu in menu_portal.get_descendants().filter(status='public'):
            url = _treatment_url(domain, menu.get_absolute_url())
            if not url:
                continue
            results.append({'url': url,
                            'modified_date': None,
                            'priority': PRIORITY_CHOICES['high']})
    if with_sections:
        sections = BaseSection.objects.published()
        for section in sections:
            url = _treatment_url(domain, section.public_link())
            if not url:
                continue
            results.append({'url': url,
                            'modified_date': None,
                            'priority': PRIORITY_CHOICES['high']})
            if with_menu_section:
                menu_section = section.main_menu
                for menu in menu_section.get_descendants().filter(status='public'):
                    url = _treatment_url(domain, menu.get_absolute_url())
                    if not url:
                        continue
                    results.append({'url': url,
                                    'modified_date': None,
                                    'priority': PRIORITY_CHOICES['medium']})
    if with_contents:
        contents = BaseContent.objects.published()
        for content in contents:
            url = _treatment_url(domain, content.public_link())
            if not url:
                continue
            results.append({'url': url,
                            'modified_date': content.modification_date,
                            'priority': PRIORITY_CHOICES['low']})
    return render_to_string("seo/sitemap.xml", {'results': results})
