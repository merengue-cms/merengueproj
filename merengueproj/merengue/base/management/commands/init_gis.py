from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = u"Initialize gis on database"

    option_list = BaseCommand.option_list + (
    )

    args = ""

    def handle(self, *fixtures, **options):
        from django.contrib.gis.gdal import SpatialReference
        from django.contrib.gis.utils import add_postgis_srs
        # adding the Google Projection Merkator
        add_postgis_srs(SpatialReference(900913))
