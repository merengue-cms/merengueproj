from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.forum.views',
    url(r'^$', 'forum_index', name='forum_index'),
    url(r'^(?P<forum_slug>[\w-]+)/$', 'forum_view', name='forum_view'),
    url(r'^(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/$', 'thread_view', name='thread_view'),
)
