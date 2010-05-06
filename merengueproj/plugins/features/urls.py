from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.features.views',
    url(r'^$', 'features_index', name='features_index'),
    url(r'^(?P<features_slug>[\w-]+)/$', 'features_view',
        name='features_view'),
)
