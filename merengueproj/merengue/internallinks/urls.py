from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('merengue.internallinks.views',
    url(r'^$', 'internal_links_search', name='internal_links_search'),
)
