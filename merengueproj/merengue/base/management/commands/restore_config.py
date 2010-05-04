# -*- coding: utf-8 -*-
import os
import zipfile

from django.core.management.base import CommandError, LabelCommand
from merengue.base.management.base import MerengueCommand
from merengue.base.utils import restore_config


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
        restore_config(zip_config) #hay que evitar esto: asi el comando funciona, pero la idea es que no sea necesario nada mas que un argumento, el archivo .zip en sí. zip_config se ha agregado para que funcione el comando. debe de haber algo mal hecho, es posible que el codigo se haya "partido" mal.
