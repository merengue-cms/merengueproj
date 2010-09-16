# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand

from plugins.filebrowser.models import Repository


class Command(NoArgsCommand):
    help = u"Create directories that not exists and there are in database"

    def handle_noargs(self, **options):
        filebrowsers = Repository.objects.all()
        for i in filebrowsers:
            path = i.get_root_path()
            if not i.check_dir(path):
                print "%s not exists; creating..." % path
                i.create_dir(path)
