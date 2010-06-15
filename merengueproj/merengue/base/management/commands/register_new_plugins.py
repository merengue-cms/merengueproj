# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.core.cache import cache as django_cache

from merengue.base.management.base import MerengueCommand
from merengue.pluggable import register_plugin
from merengue.pluggable.utils import get_plugins_dir
from merengue.pluggable.models import RegisteredPlugin

from johnny import cache


class Command(MerengueCommand):
    help = "Register new plugins found in plugins directory"
    requires_model_validation = True

    def handle(self, **options):
        for plugin_dir in os.listdir(os.path.join(settings.BASEDIR, get_plugins_dir())):
            register_plugin(plugin_dir)
        # cache invalidation
        query_cache_backend = cache.get_backend()(django_cache)
        query_cache_backend.patch()
        cache.invalidate(RegisteredPlugin._meta.db_table)
