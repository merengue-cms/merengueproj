from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('merengue.places.views',
    url(r'^ajax/nearby/$', 'places_ajax_nearby', name='places_ajax_nearby'),
    url(r'^merengue_content_info/(?P<content_type>\d+)/(?P<content_id>\d+)/$', 'content_info', name='content_info'),
)
