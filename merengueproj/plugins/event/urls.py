from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.event.views',
    url(r'^(?P<event_slug>[\w-]+)/$', 'event_view', name='event_view'),
    url(r'^events/(?P<year>[\d-]+)/(?P<month>[\d-]+)/(?P<day>[\d-]+)/$', 'event_list', name='event_list'),
    url(r'^calendar/ajax/$', 'events_calendar', name='events_calendar'),
)
