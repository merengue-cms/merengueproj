from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.fooplugin.views',
    url(r'^$', 'foomodel_index', name='foomodel_index'),
)
