# -*- coding: utf-8 -*-

import sys

from django.core.management.base import BaseCommand

from merengue.base.models import BaseContent


class Command(BaseCommand):
    help = 'Fires the save method of all BaseContent objects in order to update its fields if changes were done in the code'

    def handle(self, *args, **options):
        content_list = BaseContent.objects.all()
        count = content_list.count()
        index = 0
        for content in content_list:
            index += 1
            sys.stdout.write('Saving BaseContent [%s/%s]\r' % (index, count))
            sys.stdout.flush()
            instance = content.get_real_instance()
            instance.save()
        print
