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

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag
from transmeta import TransMeta, get_fallback_fieldname, get_real_fieldname

from merengue.pluggable.utils import get_plugin


class ITag(Tag):

    __metaclass__ = TransMeta

    tag_name = models.CharField(max_length=50, verbose_name=_('tag name'))

    class Meta:
        translate = ('tag_name', )
        verbose_name = _('Internazionalized Tag')
        verbose_name_plural = _('Internazionalized Tags')


def create_itag(sender, instance, **kwargs):
    # ensure that tag.name is the itag.tag_name to avoid integrity errors
    # because tag.name is unique (see #1201).
    instance.name = instance.tag_name


def create_itag_from_tag(sender, instance, **kwargs):

    try:
        instance.itag
    except ITag.DoesNotExist:
        itag = ITag(tag_ptr=instance)
        lang = get_plugin('itags').get_config().get('main_language', None)
        lang = lang and lang.value or None
        if lang in dict(settings.LANGUAGES).keys():
            setattr(itag, get_real_fieldname('tag_name', lang), instance.name)
        else:
            setattr(itag, get_fallback_fieldname('tag_name'), instance.name)
        itag.save_base(raw=True)

models.signals.pre_save.connect(create_itag, sender=ITag)
models.signals.post_save.connect(create_itag_from_tag, sender=Tag)
