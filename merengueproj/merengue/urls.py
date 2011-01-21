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

# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import *

js_info_dict = {
        'packages': ('django.conf', ),
}

handler404 = 'merengue.perms.defaults.page_not_found'

urlpatterns = patterns('',
    # actions
    (r'^actions/', include('merengue.action.urls')),

    # blocks
    (r'^blocks/', include('merengue.block.urls')),

    # login and logout
    url(r'^login/$', 'merengue.portal.views.login', name="merengue_login"),
    url(r'^logout/$', 'merengue.portal.views.logout', name="merengue_logout"),
    url(r'^password/reset/$', 'merengue.portal.views.password_reset', name="password_reset"),
    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'merengue.portal.views.password_reset_confirm', name="password_reset_confirm"),
    url(r'^password/reset/done/$', 'merengue.portal.views.password_reset_complete', name="password_reset_complete"),

    # base urls
    (r'^base/', include('merengue.base.urls')),

    # multimedia
    (r'^multimedia/', include('merengue.multimedia.urls')),

    # section
    (r'^sections/', include('merengue.section.urls')),

    # menu
    url(r'^menu(/[\w\-]+)*/(?P<menu_slug>[\w-]+)/$', 'merengue.section.views.menu_view', name='menu_view'),

    # tinyimages
    (r'^tinyimages/', include('tinyimages.urls')),

    # i18n applications
    url(r'^transhette/', include('transhette.urls')),
    url(r'^inlinetrans/', include('inlinetrans.urls')),
    (r'^i18n/setlang/$', 'merengue.portal.views.set_language'),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

    # collaborative views
    (r'^collab/', include('merengue.collab.urls')),

    # searchforms
    (r'^searchform/', include('searchform.urls')),
    (r'^searchform_jsi18n/', include('searchform.jsi18n_urls')),

    # ajax_select
    (r'^ajax_select/', include('ajax_select.urls')),

   # genericforeignkey
    (r'^genericforeignkey/', include('genericforeignkey.urls')),

    # collections
    (r'^collection/', include('merengue.collection.urls')),

    # notification
    (r'^notification/', include('notification.urls')),

    # other
    (r'^internal-links/', include('merengue.internallinks.urls')),
    (r'^threadedcomments/', include('threadedcomments.urls')),
    url(r'^invalidate/$', 'merengue.portal.views.invalidate_cache', name='invalidate_cache'),
    (r'^inplaceeditform/', include('inplaceeditform.urls')),
    (r'^reports/', include('autoreports.urls')),
    (r'^captcha/', include('captcha.urls')),
)

if settings.USE_GIS:
    # places
    urlpatterns += patterns('', (r'^places/', include('merengue.places.urls')), )
