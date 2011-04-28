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

from django.contrib.auth.views import logout as django_logout
from django.utils.translation import gettext as _

from djangosaml2.views import logout, logout_service

from cmsutils.log import send_info

from plugins.saml2.saml_config_loader import merengue_config_loader


def merengue_logout(request):
    if '_saml2_subject_id' in request.session:
        return logout(request, config_loader=merengue_config_loader)
    else:
        return django_logout(request)


def merengue_logout_service(request):
    """Do the logout and then send a message to the user"""
    response = logout_service(request, config_loader=merengue_config_loader,
                              next_page='/')
    if 'SAMLResponse' in request.GET:  # we started the logout
        send_info(request, _('Thank you for your visit'))
    return response
