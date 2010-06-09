import os
import ConfigParser

from django.conf import settings
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from south.signals import post_migrate

from merengue.theming import get_theme_path
from merengue.theming.managers import ThemeManager


class Theme(models.Model):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    installed = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    directory_name = models.CharField(_('directory name'), max_length=100)

    class Meta:
        db_table = 'themes_theme'

    objects = ThemeManager()

    def __unicode__(self):
        return self.name

    def get_path(self):
        """ get theme template path """
        return get_theme_path(self.directory_name)

    def get_theme_media_url(self):
        return '%sthemes/%s/' % (settings.MEDIA_URL, self.directory_name)

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


def check_for_themes(sender, **kwargs):
    from merengue.theming.checker import check_themes
    check_themes()


signals.post_save.connect(check_for_duplicated_active_themes, sender=Theme)
post_migrate.connect(check_for_themes)
