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

import datetime
from django.conf import settings
from django.db import models
from django.db.models import signals
from django.template import defaultfilters
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _


class JSONDateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        return json.JSONEncoder.default(self, obj)


class JSONField(models.TextField):
    description = _("Data that serializes and deserializes into and out of JSON.")

    def _dumps(self, data):
        return JSONDateEncoder().encode(data)

    def _loads(self, str):
        return json.loads(str, encoding=settings.DEFAULT_CHARSET)

    def _get_val_from_obj(self, obj):
        """ to do object serialization (i.e. to save fixtures) """
        if obj is not None:
            return self._dumps(super(JSONField, self)._get_val_from_obj(obj))
        else:
            return self.get_default()

    def get_internal_type(self):
        return 'TextField'

    def pre_save(self, model_instance, add):
        return self._dumps(getattr(model_instance, self.attname, None))

    def contribute_to_class(self, cls, name):
        self.class_name = cls
        super(JSONField, self).contribute_to_class(cls, name)
        signals.post_init.connect(self.post_init)

        def get_json(model_instance):
            return self._dumps(getattr(model_instance, self.attname, None))
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model_instance, json):
            return setattr(model_instance, self.attname, self._loads(json))
        setattr(cls, 'set_%s_json' % self.name, set_json)

    def post_init(self, **kwargs):
        if 'sender' in kwargs and 'instance' in kwargs:
            instance, sender = kwargs['instance'], kwargs['sender']
            if issubclass(sender, self.class_name) and hasattr(instance, self.attname):
                value = self.value_from_object(instance)
                if not value:
                    value = None
                elif isinstance(value, basestring):
                    value = self._loads(value)
                setattr(instance, self.attname, value)


def get_ordered_parents(model):
    """
    Returns a list of all the ancestor of this model as a list.
    """
    result = []
    for parent in model._meta.parents:
        result.append(parent)
        result.extend(get_ordered_parents(parent))
    return result


class AutoSlugField(models.SlugField):

    def __init__(self, autofromfield, *args, **kwargs):
        self.force_on_edit = kwargs.pop('force_on_edit', False)
        self.unique_on_parent_model = kwargs.pop('unique_on_parent_model', False)
        super(AutoSlugField, self).__init__(*args, **kwargs)
        self.autofromfield = autofromfield
        self.editable = kwargs.get('editable', False)

    def sluggify(self, name, objects):
        slug = defaultfilters.slugify(name)
        slug_num = slug
        n = 2
        filter_param = '%s__exact' % self.name
        filters = {filter_param: slug_num}
        while objects.filter(**filters):
            slug_num = slug + u'-%s' % n
            filters[filter_param] = slug_num
            n += 1
        return slug_num

    def _get_manager(self, instance):
        instance_model = instance.__class__
        if not self.unique_on_parent_model:
            return instance_model._default_manager
        models_to_iterate = [instance_model] + get_ordered_parents(instance_model)
        for model in models_to_iterate:
            if self in model._meta.local_fields:
                return model._default_manager

    def pre_save(self, instance, add):
        value = getattr(instance, self.autofromfield)

        objects_manager = self._get_manager(instance)

        if not instance.id:
            slug = self.sluggify(value, objects_manager.all())
        elif add or self.force_on_edit:
            slug = self.sluggify(value, objects_manager.exclude(id=instance.id))
        else:
            slug = getattr(instance, self.name)
        setattr(instance, self.name, slug)
        return slug

    def get_internal_type(self):
        return 'SlugField'
