from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.news.views',
    url(r'^$', 'news_index', name='news_index'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'news_by_date'),
    url(r'^(?P<newsitem_slug>[\w-]+)/$', 'newsitem_view', name='newsitem_view'),
    url(r'^ajax/(?P<newscategory_slug>[\w-]+)/$', 'newsitem_by_category_view', name='newsitem_by_category_view'),
)
