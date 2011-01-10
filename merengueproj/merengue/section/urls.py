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

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('merengue.section.views',
    url(r'ajax/save_menu_order/$', 'save_menu_order', name='save_menu_order'),
    url(r'ajax/insert_section/$', 'insert_document_section_after', name='insert_document_section_after'),
    url(r'ajax/delete_section/$', 'document_section_delete', name='document_section_delete'),
    url(r'ajax/edit_section/$', 'document_section_edit', name='document_section_edit'),
    url(r'ajax/move_section/$', 'document_section_move', name='document_section_move'),
    url(r'^(?P<section_slug>[\w-]+)/$', 'section_view', name='section_view'),
    url(r'^(?P<section_slug>[\w-]+)/css/$', 'section_custom_style', name='section_custom_style'),
    url(r'^(?P<section_slug>[\w-]+)/contents/(?P<content_id>\d+)/(?P<content_slug>[\w-]+)/$', 'content_section_view', name='content_section_view'),
    url(r'^(?P<section_slug>[\w-]+)/doc/(?P<document_id>\d+)/(?P<document_slug>[\w-]+)/$', 'document_section_view', name='document_section_view'),
    url(r'^(?P<section_slug>[\w-]+)(/[\w\-]+)*/(?P<menu_slug>[\w-]+)/$', 'menu_section_view', name='menu_section_view'),
)
