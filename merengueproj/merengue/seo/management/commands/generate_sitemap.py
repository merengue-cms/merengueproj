from os import path
from optparse import make_option

from django.conf import settings

from merengue.base.management.base import MerengueCommand
from merengue.seo.utils import generate_sitemap


class Command(MerengueCommand):
    help = "Generate a XML file with the current sitemap"

    option_list = MerengueCommand.option_list + (
        make_option('-p', '--without-portal-links', action='store_true', dest='without_portal_links', default=False),
        make_option('-m', '--without-menu-portal', action='store_true', dest='without_menu_portal', default=False),
        make_option('-s', '--without-sections', action='store_true', dest='without_sections', default=False),
        make_option('-x', '--without-menu-section', action='store_true', dest='without_menu_section', default=False),
        make_option('-c', '--without-contents', action='store_true', dest='without_contents', default=False),
    )

    def handle(self, *args, **options):
        sitemap = generate_sitemap(with_portal_links=not options.get('without_portal_links'),
                                   with_menu_portal=not options.get('without_menu_portal'),
                                   with_sections=not options.get('without_sections'),
                                   with_menu_section=not options.get('without_menu_section'),
                                   with_contents=not options.get('without_contents'))
        fich = file(path.join(settings.MEDIA_ROOT, 'sitemap.xml'), 'w')
        fich.write(sitemap)
        fich.close()
