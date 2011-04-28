# Copyright (c) 2011 by Yaco Sistemas
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

from plugins.saml2.saml_config_loader import merengue_config_loader
from plugins.saml2.saml_config_loader import get_attribute_mapping
from plugins.saml2.saml_config_loader import get_create_unknown_user

urlpatterns = patterns(
    'djangosaml2.views',
    url(r'^login/$', 'login', name='saml2_login',
        kwargs=dict(config_loader=merengue_config_loader)),
    url(r'^acs/$', 'assertion_consumer_service', name='saml2_acs',
        kwargs=dict(config_loader=merengue_config_loader,
                    attribute_mapping=get_attribute_mapping,
                    create_unknown_user=get_create_unknown_user)),
    url(r'^metadata/$', 'metadata', name='saml2_metadata',
        kwargs=dict(config_loader=merengue_config_loader)),
    )

urlpatterns += patterns(
    'plugins.saml2.views',
    url(r'^logout/$', 'merengue_logout', name='saml2_logout'),
    url(r'^ls/$', 'merengue_logout_service', name='saml2_ls')
    )
