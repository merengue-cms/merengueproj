# -*- coding: utf-8 -*-

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

import re
import htmlentitydefs
from django.template import Library
from django.utils.translation import ugettext as _

register = Library()


@register.filter
def trans_yesno(value, arg=None):
    """
    Like django yesno built in filter, but with a translation call to all values
    """
    if arg is None:
        arg = _('yes,no,maybe')
    bits = arg.split(u',')
    if len(bits) < 2:
        return _(value)  # Invalid arg.
    try:
        yes, no, maybe = bits
    except ValueError:
        # Unpack list of wrong size (no "maybe" value provided).
        yes, no, maybe = bits[0], bits[1], bits[1]
    if value is None:
        return _(maybe)
    if value:
        return _(yes)
    return _(no)
trans_yesno.is_safe = False


@register.filter
def unescape_html_entities(string):
    """Converts HTML entities into unicode letters.

    Examples:

      "&aacute;".convert_accented_entities #: "á"
      "&ccedil;".convert_accented_entities #: "ç"

    """
    entities_regex = re.compile('&(' + '|'.join(htmlentitydefs.name2codepoint.keys()) + ');')
    return re.sub(
        entities_regex,
        lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]),
        string,
    )


@register.filter
def basecontent_type(obj):
    """
    Returns meta class name
    """
    return obj._meta.verbose_name
