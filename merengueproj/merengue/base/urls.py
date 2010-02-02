from django.conf.urls.defaults import patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('merengue.base.views',
    (r'^admin_redirect/(?P<content_type>\d+)/(?P<content_id>\d+)/(?P<url>.*)$', 'admin_link'),
    (r'^public_redirect/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<content_id>\d+)/$', 'public_link'),
    (r'^view/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<content_id>\d+)/(?P<content_slug>[\w-]+)/$', 'public_view'),
)
