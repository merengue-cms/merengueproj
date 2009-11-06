from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.tv.views',
    url(r'^$', 'video_index', name='video_index'),
    url(r'^(?P<video_id>\d+)/$', 'video_view', name='video_view'),
)
