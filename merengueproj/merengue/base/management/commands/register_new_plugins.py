# -*- coding: utf-8 -*-
import os
from django.conf import settings

from merengue.base.management.base import MerengueCommand
from merengue.pluggable import register_plugin
from merengue.pluggable.utils import get_plugins_dir


class Command(MerengueCommand):
    help = "Register new plugins found in plugins directory"
    requires_model_validation = True

    def handle(self, **options):
        for plugin_dir in os.listdir(os.path.join(settings.BASEDIR, get_plugins_dir())):
            register_plugin(plugin_dir)
