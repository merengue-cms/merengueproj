# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from merengue.base.widgets import CustomTinyMCE


class TMTemplate(models.Model):

    name = models.CharField(
        verbose_name=_('name'),
        max_length=200,
        db_index=True,
        )

    description = models.TextField(
        verbose_name=_('template description'),
        )

    content = models.TextField(
        verbose_name=_('template content'),
        )

    class Meta:
        verbose_name = _('Tiny MCE Template')
        verbose_name_plural = _('Tiny MCE Templates')

    def __unicode__(self):
        return self.name


CustomTinyMCE.contribute_adding_to_setting('plugins', 'template')
CustomTinyMCE.contribute_adding_to_setting('theme_advanced_buttons2', 'template')
CustomTinyMCE.contribute_adding_new_setting('template_external_list_url', '/tmtemplates/template_list.js')
