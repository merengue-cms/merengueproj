from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.event.views',
    url(r'^(?P<event_slug>[\w-]+)/$', 'event_view', name='event_view'),
)
