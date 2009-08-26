from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('merengue.action.views',
    url(r'site/(?P<name>.*)/', 'site_action', name='site_action'),
    url(r'user/(?P<username>.*)/(?P<name>.*)/', 'user_action', name='user_action'),
    url(r'content/(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<name>.*)/', 'content_action', name='content_action'),
)
