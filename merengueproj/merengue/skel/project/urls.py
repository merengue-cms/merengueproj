# -*- coding: utf-8 -*-
# don't touch this "import *" is necesary for urlresolvers works
from django.conf.urls.defaults import *
from django.conf import settings

from merengue.base import admin
from merengue.urls import *

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
