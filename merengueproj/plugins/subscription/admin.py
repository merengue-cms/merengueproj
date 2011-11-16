# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django import forms

from merengue.base.admin import PluginAdmin, RelatedModelAdmin
from merengue.base.models import BaseContent
from plugins.subscription.models import Subscribable, BaseSubscription
from plugins.subscription.forms import SubscribableAdminForm


class SubscribableAdmin(RelatedModelAdmin):
    related_field = 'content'
    change_form_template = 'admin/subscription/subscribable/change_form.html'
    form = SubscribableAdminForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(SubscribableAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'class_name':
            field.widget = forms.Select(choices=tuple(self.get_choices_class_name(BaseSubscription)))
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


class BaseSubscriptionAdmin(PluginAdmin):
    list_filter = ('subscribable', )


def register(site):
    """ Merengue admin registration callback """
    site.register_related(Subscribable, SubscribableAdmin, related_to=BaseContent)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister_related(Subscribable, SubscribableAdmin, related_to=BaseContent)
