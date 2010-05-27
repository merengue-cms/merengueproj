# -*- coding: utf-8 -*-
from merengue.base.management.base import MerengueCommand
from merengue.pluggable.checker import mark_broken_plugins


class Command(MerengueCommand):

    help = "Mark all broken plugins"
    label = 'config name'
    requires_model_validation = True
    can_import_settings = False

    def handle(self, **options):
        mark_broken_plugins()
