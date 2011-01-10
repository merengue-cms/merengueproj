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

urlpatterns = patterns('merengue.collab.views',
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/$', 'ajax_admin_comments', name='ajax_admin_comments'),
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/list/$', 'ajax_list_comments', name='ajax_list_comments'),
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/add/$', 'ajax_add_comment', name='ajax_add_comment'),
    url(r'ajax/comments/(?P<comment_id>\d+)/revise/$', 'ajax_revise_comment', name='ajax_revise_comment'),
    url(r'ajax/comments/(?P<comment_id>\d+)/$', 'ajax_get_comment', name='ajax_get_comment'),
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/count/$', 'ajax_num_comments', name='ajax_num_comments'),
    # Translation
    url(r'ajax/translation/(?P<content_type_id>\d+)/(?P<content_id>\d+)/(?P<field>\w+)/$', 'ajax_admin_translation', name='ajax_admin_translation'),
    url(r'ajax/translation/(?P<content_type_id>\d+)/(?P<content_id>\d+)/(?P<field>\w+)/lang/$', 'ajax_edit_translation', name='ajax_edit_translation'),
    url(r'ajax/translation/(?P<content_type_id>\d+)/(?P<content_id>\d+)/(?P<field>\w+)/lang/(?P<language_id>\w+)/$', 'ajax_edit_translation', name='ajax_edit_translation'),
)
