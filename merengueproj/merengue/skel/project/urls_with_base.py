from django.conf import settings
from django.conf.urls.defaults import patterns
from merengue.urls import *  # pyflakes:ignore


urlpatterns = patterns('',
    (r'^%s' % settings.BASE_URL[1:], include('{{ project_name }}.urls')),
)
