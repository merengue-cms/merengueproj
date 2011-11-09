from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from merengue.base.models import BaseContent
from merengue.portal.models import PortalLink
from merengue.section.models import Menu, BaseSection
from merengue.urlresolvers import get_url_default_lang

PRIORITY_CHOICES = {'low': 0.3,
                    'medium': 0.7,
                    'high': 1}


def true_by_default(param):
    return param is None or param == '1'


def false_by_default(param):
    return param == '1'


def _treatment_url(domain, url):
    if url and url.startswith('/'):
        return "%s%s" % (domain, url)
    return url


def generate_sitemap(with_portal_links=True, with_menu_portal=True,
                     with_sections=True, with_menu_section=True,
                     with_contents=True, priority_choices=None):
    priority_choices = priority_choices or PRIORITY_CHOICES
    domain = 'http://%s' % Site.objects.get_current().domain
    _treatment_url_microsites = False
    if with_sections or with_contents:
        if 'plugins.microsite.middleware.MicrositeMiddleware' in settings.MIDDLEWARE_CLASSES:
            _treatment_url_microsites = True
            from plugins.microsite.config import PluginConfig
            microsite_prefixes = PluginConfig.url_prefixes[0][0]
            microsite_prefix = microsite_prefixes.get(get_url_default_lang(),
                               microsite_prefixes.get('en', '/microsite/'))
            microsite_replace = '%s/%s' % (domain, microsite_prefix)

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
            section = section.get_real_instance()
            url = _treatment_url(domain, section.public_link())
            if not url:
                continue
            if _treatment_url_microsites and url.startswith(microsite_replace):
                url = url.replace(microsite_replace, domain)
            results.append({'url': url,
                            'modified_date': None,
                            'priority': PRIORITY_CHOICES['high']})
            if with_menu_section:
                menu_section = section.main_menu
                for menu in menu_section.get_descendants().filter(status='public'):
                    url = _treatment_url(domain, menu.get_absolute_url())
                    if not url:
                        continue
                    if _treatment_url_microsites and url.startswith(microsite_replace):
                        url = url.replace(microsite_replace, domain)
                    results.append({'url': url,
                                    'modified_date': None,
                                    'priority': PRIORITY_CHOICES['medium']})
    if with_contents:
        class_names = ('basesection',) + settings.SMAP_EXCLUDE_CLASS_NAME
        subclasses = BaseSection.get_subclasses()
        class_names += tuple([subclass.__name__.lower() for subclass in subclasses])
        contents = BaseContent.objects.published().exclude(class_name__in=class_names)
        for content in contents:
            content = content.get_real_instance()
            url = _treatment_url(domain, content.public_link())
            if not url:
                continue
            if _treatment_url_microsites and url.startswith(microsite_replace):
                url = url.replace(microsite_replace, domain)
            results.append({'url': url,
                            'modified_date': content.modification_date,
                            'priority': PRIORITY_CHOICES['low']})
    return render_to_string("seo/sitemap.xml", {'results': results})
