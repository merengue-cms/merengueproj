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

from django.conf.urls.defaults import patterns
from merengue.urlresolvers import merengue_url as url

urlpatterns = patterns('merengue.block.views',
    url(r'^$', 'blocks_index', name='blocks_index'),
    url({'en': r'order/ajax/',
         'es': r'orden/ajax/'},
        'blocks_reorder', name='blocks_reorder'),
    url(r'ajax/config/(?P<block_id>\d+)$', 'generate_blocks_configuration',
        name='generate_blocks_configuration'),
    url(r'ajax/config_for_content/(?P<block_id>\d+)$', 'generate_blocks_configuration_for_content',
        name='generate_blocks_configuration_for_content'),
    url(r'ajax/remove-block/(?P<block_id>\d+)/$', 'remove_block',
        name='remove_block'),
    url(r'ajax/invalidate-cache/(?P<block_id>\d+)/$', 'invalidate_cache',
        name='invalidate_cache'),
    url(r'ajax/add-block/$', 'add_block',
        name='add_block'),
)
