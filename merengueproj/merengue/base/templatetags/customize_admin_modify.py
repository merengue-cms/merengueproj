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

from django import template

register = template.Library()


def customize_submit_row(context, prefix=''):
    opts = context['opts']
    change = context['change']
    model_admin = context['model_admin']
    is_popup = context['is_popup']
    save_as = context['save_as']
    is_foreign_model = context.get('is_foreign_model', False)
    is_related_one_to_one_admin = getattr(model_admin, 'one_to_one', False)
    current_body_field = context.get('current_body_field', False)
    return {
        'no_save': context.get('original', None) and getattr(context['original'], 'no_changeable', False),
        'is_foreign_model': is_foreign_model,
        'current_body_field': current_body_field,
        'onclick_attrib': (opts.get_ordered_objects() and change
                            and 'onclick="submitOrderForm();"' or ''),
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and (change or context['show_delete'])),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and
                            not is_popup and (not save_as or context['add']) and
                            not is_related_one_to_one_admin,
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': not is_related_one_to_one_admin,
        'prefix': prefix}
customize_submit_row = register.inclusion_tag('admin/customize_submit_line.html', takes_context=True)(customize_submit_row)
