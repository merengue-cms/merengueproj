from os import path

from django.conf import settings

from merengue.base.management.base import MerengueCommand
from merengue.seo.utils import generate_sitemap


class Command(MerengueCommand):
    help = "Generate a XML file with the current sitemap"

    def handle(self, **options):
        sitemap = generate_sitemap()
        fich = file(path.join(settings.MEDIA_ROOT, 'sitemap.xml'), 'w')
        fich.write(sitemap)
        fich.close()
