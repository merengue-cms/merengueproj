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

from django.db.models import BooleanField, CharField, Model
from django.utils.translation import ugettext_lazy as _


class Redirect(Model):
    """
    Redirect model. Almost the same as django Redirect
    """
    CODE_CHOICES = (
        ('p', '301'),  # Moved Permanently
        ('f', '302'),  # Found
    )

    old_path = CharField(_('redirect from'), max_length=200, db_index=True,
        help_text=_("This should be an absolute path, excluding the domain \
                                        name. Example: '/events/search/'."))
    new_path = CharField(_('redirect to'), max_length=200, blank=True,
        help_text=_("This can be either an absolute path (as above) or a full \
                                                URL starting with 'http://'."))
    is_active = BooleanField()
    redirection_code = CharField(max_length=1, choices=CODE_CHOICES)

    def is_permanent(self):
        """
        Property to chect if edirect is permanent
        """
        return self.redirection_code == 'p'
    is_permanent = property(is_permanent)

    class Meta:
        verbose_name = _('redirect', )
        verbose_name_plural = _('redirects', )
        ordering = ('old_path', )

    def __unicode__(self):
        return "%s ---> %s" % (self.old_path, self.new_path)
