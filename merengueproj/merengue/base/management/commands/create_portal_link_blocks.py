# -*- coding: utf-8 -*-

from copy import deepcopy

from django.conf import settings
from django.core.management.base import BaseCommand

from merengue.block.models import RegisteredBlock


class Command(BaseCommand):
    help = 'Creates the new PortalLinksBlock instances needed'

    def handle(self, *args, **options):
        # Primero, "actualizamos" los antiguos bloques
        # y creamos los indicados en el settings
        old_blocks = RegisteredBlock.objects.filter(
            class_name__in=['PrimaryLinksBlock', 'SecondaryLinksBlock'])

        base_portal_block = RegisteredBlock(
            active=True, category=u'block', class_name=u'PortalLinksBlock',
            module=u'plugins.core.blocks')

        for key, value in settings.PORTAL_LINK_CATEGORIES:
            place = settings.PORTAL_LINK_POSITIONS[key]
            copied_portal_block = deepcopy(base_portal_block)
            try:
                old_block = old_blocks.get(name='%slinks' % key)
                copied_portal_block.placed_at = place
                copied_portal_block.order = old_block.order
                old_block.delete()
            except RegisteredBlock.DoesNotExist:
                copied_portal_block.placed_at = place
            if not RegisteredBlock.objects.filter(name='%slinks' % key):
                copied_portal_block.name = '%slinks' % key
                copied_portal_block.config = {'category': key}
                copied_portal_block.id = None  # to force new instance
                copied_portal_block.save()
