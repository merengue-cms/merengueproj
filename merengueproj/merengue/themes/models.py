import os
import ConfigParser

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from merengue.themes import get_theme_path
from merengue.themes.managers import ThemeManager


class Theme(models.Model):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    installed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    directory_name = models.CharField(_('directory name'), max_length=100)

    objects = ThemeManager()

    def __unicode__(self):
        return self.name

    def get_path(self):
        """ get theme template path """
        return get_theme_path(self.directory_name)

    def update_from_fs(self, commit=True):
        """ update theme info from filesystem """
        theme_info_file = os.path.join(self.get_path(), 'theme.info')
        if os.path.isfile(theme_info_file):
            config = ConfigParser.ConfigParser()
            config.read(theme_info_file)
            theme_name = config.get(ConfigParser.DEFAULTSECT, 'name', self.directory_name)
            theme_description = config.get(ConfigParser.DEFAULTSECT, 'description', '')
        else:
            theme_name = self.directory_name
            theme_description = ''
        self.name = theme_name
        self.description = theme_description
        if commit:
            self.save()


def check_for_duplicated_active_themes(sender, instance, **kwargs):
    if instance.active:
        for theme in Theme.objects.filter(active=True).exclude(id=instance.id):
            theme.active = False
            theme.save()

signals.post_save.connect(check_for_duplicated_active_themes, sender=Theme)
