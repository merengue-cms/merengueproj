from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('merengue.uitools.views',
    url(r'^save/$', 'merengue_save_ajax', name='inplace_merengue_save'),
)
