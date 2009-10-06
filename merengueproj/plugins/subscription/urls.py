from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('plugins.subscription.views',
    url(r'^(?P<basecontent_slug>[\w-]+)/$', 'subscription_form', name='subscription_form'),
)
