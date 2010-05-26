from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.tv.views',
    url(r'^$', 'tv_index', name='tv_index'),
    url(r'^video/(?P<video_id>\d+)/$', 'video_view', name='video_view'),
    url(r'^(?P<channel_slug>[\w-]+)/$', 'channel_view', name='channel_view'),
)
