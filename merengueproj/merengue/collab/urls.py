from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('merengue.collab.views',
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/$', 'ajax_admin_comments', name='ajax_admin_comments'),
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/$', 'ajax_admin_comments', name='ajax_admin_comments'),
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/list/$', 'ajax_list_comments', name='ajax_list_comments'),
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/add/$', 'ajax_add_comment', name='ajax_add_comment'),
    url(r'ajax/comments/(?P<comment_id>\d+)/revise/$', 'ajax_revise_comment', name='ajax_revise_comment'),
    url(r'ajax/comments/(?P<comment_id>\d+)/$', 'ajax_get_comment', name='ajax_get_comment'),
    url(r'ajax/comments/(?P<content_type_id>\d+)/(?P<content_id>\d+)/count/$', 'ajax_num_comments', name='ajax_num_comments'),
)
