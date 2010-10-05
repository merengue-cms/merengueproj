from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.forum.views',
    url(r'^$', 'forum_index', name='forum_index'),
    url(r'^change_comment_visiblity/(?P<comment_id>\d+)/$', 'forum_comment_change_visibity', name='forum_comment_change_visibity'),
    url(r'^comment_delete/(?P<comment_id>\d+)/$', 'forum_comment_delete', name='forum_comment_delete'),
    url(r'^add_comment/(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/(?P<parent_id>\d+)/$',
        'forum_comment_add', name='forum_child_comment_add'),
    url(r'^add_comment/(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/$', 'forum_comment_add', name='forum_comment_add'),
    url(r'^(?P<forum_slug>[\w-]+)/$', 'forum_view', name='forum_view'),
    url(r'^(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/$', 'thread_view', name='thread_view'),
)
