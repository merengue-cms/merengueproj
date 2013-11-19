from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('tinyimages.views',
    url(r'^file_upload/$', 'file_upload_view', name="tinyimage_file_upload_view"),
    url(r'^image/$', 'image_list', name="tinyimage_list"),
    url(r'^image/(?P<image_id>\d+)/delete/$', 'image_delete', name="tinyimage_delete"),
    url(r'^file/$', 'file_list', name="tinyfile_list"),
    url(r'^file/(?P<file_id>\d+)/delete/$', 'file_delete', name="tinyfile_delete"),
)
