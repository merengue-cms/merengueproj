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

import os.path

from django.contrib.sites.models import Site

import saml2
import saml2.config

from merengue.pluggable.utils import get_plugin

from plugins.saml2.models import IdentityProvider, ContactPerson, Organization


BASEDIR = os.path.dirname(os.path.abspath(__file__))


def split_str(attribute_str):
    if attribute_str:
        return [part.strip() for part in attribute_str.split(",")]


def get_idps():
    return dict([(idp.entity_id, {
                    'single_sign_on_service': {
                        idp.single_sign_on_service_binding: idp.single_sign_on_service_url,
                        },
                    'single_logout_service': {
                        idp.single_logout_service_binding: idp.single_logout_service_url,
                        },
                    }) for idp in IdentityProvider.objects.all()])


def get_metadata_files():
    return [idp.metadata.path for idp in IdentityProvider.objects.all()]


def get_contact_people():
    return [{'given_name': cp.given_name,
             'sur_namne': cp.sur_name,
             'company': cp.company,
             'email_address': cp.email_address,
             'contact_type': cp.contact_type,
             } for cp in ContactPerson.objects.all()]


def get_organization():
    organizations = Organization.objects.all()
    if organizations.count() > 0:
        return  {
            'name': [(o.name, o.language) for o in organizations],
            'display_name': [(o.display_name, o.language) for o in organizations],
            'url': [(o.url, o.language) for o in organizations],
            }
    else:
        return {}


def merengue_config_loader():
    site = Site.objects.get_current()
    site_url = 'http://' + site.domain + '/saml2/'
    entity_id = site_url + 'metadata/'
    plugin_config = get_plugin('saml2').get_config()
    config_dict = {
        # basic, mandatory stuff
        'xmlsec_binary': plugin_config['xmlsec_binary'].get_value(),
        'entityid': entity_id,
        'attribute_map_dir': os.path.join(BASEDIR, 'attribute-maps'),

        # this block states what services we provide
        'service': {
            'sp': {  # we are just a lonely SP
                'name': plugin_config['entity_name'].get_value(),
                'endpoints': {
                    'assertion_consumer_service': [
                        (site_url + 'acs/', saml2.BINDING_HTTP_POST),
                        ],
                    'single_logout_service': [
                        (site_url + 'ls/', saml2.BINDING_HTTP_REDIRECT),
                        ],
                    },
                'idp': get_idps(),
                },
            },

        'metadata': {
            'local': get_metadata_files(),
            },

        'debug': 1,

        # certificates
        'key_file': plugin_config['key_file_path'].get_value(),
        'cert_file': plugin_config['cert_file_path'].get_value(),

        # These fields are only used when generating the metadata
        'contact_person': get_contact_people(),
        'organization': get_organization(),
        'valid_for': plugin_config['valid_for'].get_value(),  # hours
        }

    required_attrs = split_str(plugin_config['required_attributes'].get_value())
    if required_attrs:
        config_dict['service']['sp']['required_attributes'] = required_attrs

    optional_attrs = split_str(plugin_config['optional_attributes'].get_value())
    if optional_attrs:
        config_dict['service']['sp']['optional_attributes'] = optional_attrs

    sp_config = saml2.config.SPConfig()
    sp_config.load(config_dict)
    return sp_config


def get_attribute_mapping():
    plugin_config = get_plugin('saml2').get_config()
    mapping = {
        'username': plugin_config['username_attribute'].get_value(),
        'first_name': plugin_config['first_name_attribute'].get_value(),
        'last_name': plugin_config['last_name_attribute'].get_value(),
        'email': plugin_config['email_attribute'].get_value(),
        }
    # reverse the mapping
    return dict([(v, k) for k, v in mapping.items() if v])


def get_create_unknown_user():
    return True
