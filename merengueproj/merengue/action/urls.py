from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('merengue.action.views',
    url(r'(?P<name>.*)/', 'dispatcher', name='actions_dispatcher'),
)
