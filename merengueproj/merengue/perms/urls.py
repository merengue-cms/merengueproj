from django.conf.urls.defaults import patterns
from merengue.urlresolvers import merengue_url as url


urlpatterns = patterns('merengue.perms.views',
    url({'en': r'^access-request/$',
         'es': r'^peticion-de-acceso/$'},
        'access_request', name='access_request'),
)
