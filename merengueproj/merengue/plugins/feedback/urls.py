from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.feedback.views',
    url(r'^send_comment/(?P<content_type>\d+)/(?P<content_id>\d+)/(?P<parent_id>\d+)/$',
        'content_comment_add', name='comment_add_parent'),
    url(r'^send_comment/(?P<content_type>\d+)/(?P<content_id>\d+)/$', 'content_comment_add', name='comment_add'),
    url(r'^change_comment_visiblity/(?P<comment_id>\d+)/$', 'content_comment_change_visibity', name='comment_change_visibity'),
    url(r'^content_comment_delete/(?P<comment_id>\d+)/$', 'content_comment_delete', name='comment_delete'),
)
