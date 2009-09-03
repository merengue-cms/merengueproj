from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('plugins.feedback.views',
    (r'^comments/', include('django.contrib.comments.urls')),
    url(r'^$', 'feedback_index', name='feedback_index'),
)
