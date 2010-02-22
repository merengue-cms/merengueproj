# -*- coding: utf-8 -*-
import ConfigParser
import os
import zipfile

from django.db import connection, transaction
from django.core import serializers
from django.core.management.base import CommandError, LabelCommand
from django.core.management.color import no_style

from merengue.action.models import RegisteredAction
from merengue.block.models import RegisteredBlock
from merengue.base.management.base import MerengueCommand
from merengue.plugins.models import RegisteredPlugin
from merengue.registry import RegisteredItem
from merengue.themes.models import Theme


class Command(LabelCommand, MerengueCommand):

    option_list = LabelCommand.option_list
    help = "Restore merengue site configuration from a zip file"
    args = "[config_name]"
    label = 'config name'
    requires_model_validation = True
    can_import_settings = False

    def handle_label(self, config_name, **options):
        if (not os.path.isfile(config_name) or
            not zipfile.is_zipfile(config_name)):
            raise CommandError("No such zip file \"%s\"" % config_name)
        try:
            zip_config = zipfile.ZipFile(config_name, "r",
                                         compression=zipfile.ZIP_DEFLATED)
        except zipfile.BadZipFile, zipfile.LargeZipFile:
            raise CommandError("Bad or too large zip file \"%s\"" \
                               % config_name)
        config = self.get_config(zip_config)
        restore_all = (config.get("mode", "fixtures") == "all")
        version = config.get("version", "MERENGUE_VERSION")
        # TODO: Implement method to get current merengue version
        if "MERENGUE_VERSION" != version:
            raise CommandError("Merengue version error")
        models_to_restore = (
            (RegisteredItem, "registry"),
            (RegisteredAction, "actions"),
            (RegisteredBlock, "blocks"),
            (RegisteredPlugin, "plugins"),
            (Theme, "themes"),
            (RegisteredItem, "registry"),
        )
        self.restore_models(zip_config, models_to_restore)
        if restore_all:
            # TODO: Implement "all" mode restore
            pass
        zip_config.close()
        print 'File restored successfully'

    def get_config(self, zip_config):
        """
        Extract and return a dictionary with configuration parameters
        from zipped config.ini file
        """
        config_file = zip_config.open("config.ini", "r")
        config = ConfigParser.ConfigParser()
        config.readfp(config_file)
        config_dic = {}
        config_items = config.items("main")
        # From list of tuples to dict
        [config_dic.update({item[0]: item[1]}) for item in config_items]
        return config_dic

    def restore_models(self, zip_config, models_to_restore):
        """
        Add models in tuple of tuples models_to_restore to merengue database
        (ModelClass, "file_name")
        """
        sid = transaction.savepoint()
        try:
            models = set()
            for model_to_restore in models_to_restore:
                file_name = model_to_restore[1]
                format = 'json'
                fixtures_file_name = "%s.%s" % (file_name, format)
                fixtures_data = zip_config.read(fixtures_file_name, "r")
                fixtures = serializers.deserialize(format, fixtures_data)
                has_objects = False
                for fixture in fixtures:
                    if fixture:
                        has_objects = True
                    fixture.save()
                    models.add(fixture.object.__class__)
            # HACK: If we found even one object in a fixture, we need to reset
            # the database sequences.
            if has_objects:
                self.sequence_reset_sql(models)
        except Exception, e:
            transaction.savepoint_rollback(sid)
            raise CommandError("Unable to restore models from fixtures: %s" \
                               % e)
        else:
            transaction.savepoint_commit(sid)

    def sequence_reset_sql(self, models):
        """
        Reset the database sequences
        """
        cursor = connection.cursor()
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
        if sequence_sql:
            for line in sequence_sql:
                cursor.execute(line)
