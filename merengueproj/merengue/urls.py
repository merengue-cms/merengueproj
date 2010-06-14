# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import *

js_info_dict = {
        'packages': ('django.conf', ),
}

urlpatterns = patterns('',
    # actions
    (r'^actions/', include('merengue.action.urls')),

    # blocks
    (r'^blocks/', include('merengue.block.urls')),

    # login and logout
    url(r'^login/$', 'merengue.portal.views.login', name="merengue_login"),
    url(r'^logout/$', 'merengue.portal.views.logout', name="merengue_logout"),

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

    # other
    (r'^internal-links/', include('merengue.internallinks.urls')),
    (r'^threadedcomments/', include('threadedcomments.urls')),
    url(r'^invalidate/$', 'merengue.portal.views.invalidate_cache', name='invalidate_cache'),
    (r'^inplaceeditform/', include('inplaceeditform.urls')),
    (r'^reports/', include('autoreports.urls')),
)

if settings.USE_GIS:
    # places
    urlpatterns += patterns('', (r'^places/', include('merengue.places.urls')), )
