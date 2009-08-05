from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from themes.managers import ThemeManager


class Theme(models.Model):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    enabled = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    directory_name = models.CharField(_('directory name'), max_length=100)

    objects = ThemeManager()

    def __unicode__(self):
        return self.name


def check_for_duplicated_active_themes(sender, instance, **kwargs):
    if instance.active:
        for theme in Theme.objects.filter(active=True).exclude(id=instance.id):
            theme.active = False
            theme.save()

signals.post_save.connect(check_for_duplicated_active_themes, sender=Theme)
