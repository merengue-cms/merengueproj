from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.voting.views',
    url(r'^vote/(?P<object_id>\d+)/$', 'vote_object', name='vote_object'),
)
