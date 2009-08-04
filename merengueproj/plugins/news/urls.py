from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.news.views',
    url(r'^$', 'news_index', name='news_index'),
)
