from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.microsite.views',
    url(r'^(?P<microsite_slug>[\w-]+)/$', 'microsite_view', name='microsite_view'),
)
