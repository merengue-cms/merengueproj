from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('internallinks.views',
    url(r'^$', 'internal_links_search', name='internal_links_search'),
    url(r'^places/$', 'internal_links_places_search', name='internal_links_places_search'),
)
