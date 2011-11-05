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
from merengue.urlresolvers import merengue_url as url


js_info_dict = {
        'packages': ('django.conf',
                     'django.contrib.admin',
                    ),
}

handler404 = 'merengue.perms.defaults.page_not_found'

urlpatterns = patterns('',
    # actions
    url({'en': r'^actions/',
         'es': r'^acciones/'},
         include('merengue.action.urls')),

    # blocks
    url({'en': r'^blocks/',
         'es': r'^bloques/'},
         include('merengue.block.urls')),

    # login and logout
    url(r'^login/$', 'merengue.portal.views.login', name="merengue_login"),
    url(r'^logout/$', 'merengue.portal.views.logout', name="merengue_logout"),

    url({'en': r'^password/reset/$',
         'es': r'^contrasena/cambiar/$'},
         'merengue.portal.views.password_reset', name="password_reset"),
    url({'en': r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
         'es': r'^contrasena/cambiar/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$'},
         'merengue.portal.views.password_reset_confirm', name="password_reset_confirm"),
    url({'en': r'^password/reset/done/$',
         'es': r'^contrasena/cambiar/hecho/$'},
         'merengue.portal.views.password_reset_complete', name="password_reset_complete"),

    # base urls
    (r'^base/', include('merengue.base.urls')),

    # section
    url({'en': r'^sections/',
         'es': r'^secciones/'},
        include('merengue.section.urls')),

    # menu
    url(r'^menu(/[\w\-]+)*/(?P<menu_slug>[\w-]+)/$', 'merengue.section.views.menu_view', name='menu_view'),

    # tinyimages
    (r'^tinyimages/', include('tinyimages.urls')),

    # i18n applications
    url(r'^transhette/', include('transhette.urls')),
    url(r'^inlinetrans/', include('inlinetrans.urls')),
    (r'^i18n/setlang/$', 'merengue.portal.views.set_language'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict, name='merengue_jsi18n'),

    # collaborative views
    (r'^collab/', include('merengue.collab.urls')),

    # searchforms
    url({'en': r'^searchform/',
         'es': r'^formulario_de_busqueda/'},
         include('searchform.urls')),
    url({'en': r'^searchform_jsi18n/',
         'es': r'^formulario_de_busqueda_jsi18n/'},
        include('searchform.jsi18n_urls')),

    # ajax_select
    (r'^ajax_select/', include('ajax_select.urls')),

    # genericforeignkey
    (r'^genericforeignkey/', include('genericforeignkey.urls')),

    # collections
    url({'en': r'^collection/',
         'es': r'^coleccion/'},
        include('merengue.collection.urls')),

    # notification
    (r'^notification/', include('notification.urls')),

    # announcements
    (r'^announcements/', include('announcements.urls')),

    # perms
    url({'en': r'^perms/',
         'es': r'^permisos/'},
        include('merengue.perms.urls')),

    # other
    (r'^internal-links/', include('merengue.internallinks.urls')),
    (r'^uitools/', include('merengue.uitools.urls')),
    (r'^seo/', include('merengue.seo.urls')),
    (r'^threadedcomments/', include('threadedcomments.urls')),
    url(r'^invalidate/$', 'merengue.portal.views.invalidate_cache', name='invalidate_cache'),
    (r'^inplaceeditform/', include('inplaceeditform.urls')),
    (r'^reports/', include('autoreports.urls')),
    (r'^captcha/', include('captcha.urls')),
)

if settings.USE_GIS:
    # places
    urlpatterns += patterns('', (r'^places/', include('merengue.places.urls')), )
