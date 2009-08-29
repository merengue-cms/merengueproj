from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.event.views',
    url(r'^$', 'event_index', name='event_index'),
    url(r'^top-rated/$', 'top_events_rated', name='event_top_rated'),
    url(r'^search/$', 'event_search', name='event_search'),
    url(r'^search/quick/$', 'event_quick_search', name='event_quick_search'),
    url(r'^search/advanced/$', 'event_advanced_search', name='event_advanced_search'),
    url(r'^(?P<event_slug>[\w-]+)/$', 'event_view', name='event_view'),
)
