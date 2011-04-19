# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from merengue.base import admin
from merengue.urls import *  # pyflakes:ignore

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
     'cmsutils.views.generic.redirect_to_object'),
    (r'^admin/', include(admin.site.urls)),

    # the next admin is only used for having the reverse url running for 'admin'
    url(r'^admin/$', lambda request: '', name="admin_index"),

    # merengue URLs
    (r'^%s/' % settings.MERENGUE_URLS_PREFIX, include('merengue.urls')),

    # merengue media
    (r'^media/(.*)$', 'merengue.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    # Your project URLs. Put here all your URLS:
    (r'^$', 'website.views.index'),
)
