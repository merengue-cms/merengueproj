from django import forms

from merengue.base.admin import BaseAdmin, RelatedModelAdmin
from merengue.base.models import BaseContent
from plugins.subscription.models import Subscribable, BaseSubscription


class SubscribableAdmin(RelatedModelAdmin):
    related_field = 'content'

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(SubscribableAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'class_name':
            field.widget= forms.Select(choices=tuple(self.get_choices_class_name(BaseSubscription)))
        return field

    def get_choices_class_name(self, cls, choices=None):
        choices = choices or []
        choices = self.get_item_class_name(cls, choices)
        for subcls in cls.__subclasses__():
            self.get_choices_class_name(subcls, choices)
        return choices

    def get_item_class_name(self, cls, l=None):
        l = l or []
        l.append(('%s.%s' % (cls._meta.app_label, cls._meta.module_name),
                  cls._meta.verbose_name))
        return l


class BaseSubscriptionAdmin(BaseAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(BaseSubscription, BaseSubscriptionAdmin)
    site.register_related(Subscribable, SubscribableAdmin, related_to=BaseContent)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.register(Subscribable, SubscribableAdmin)
