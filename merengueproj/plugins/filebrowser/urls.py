# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.filebrowser.views',
    url(r'^(?P<repository_name>[\w-]+)/$', 'root', name='filebrowser_root'),
    url(r'^(?P<repository_name>[\w-]+)/listing/$', 'listing', name='filebrowser_root_listing'),
    url(r'^(?P<repository_name>[\w-]+)/listing/(?P<path>.*)$', 'listing', name="filebrowser_dir_listing"),
    url(r'^(?P<repository_name>[\w-]+)/download/(?P<path>.*)$', 'download', name='filebrowser_download'),
    url(r'^(?P<repository_name>[\w-]+)/upload/(?P<path>.*)$', 'upload', name='filebrowser_upload'),
    url(r'^(?P<repository_name>[\w-]+)/create/folder/(?P<path>.*)$', 'createdir', name='filebrowser_createdir'),
    url(r'^(?P<repository_name>[\w-]+)/action/(?P<path>.*)$', 'action', name='filebrowser_action'),

    # documents
    url(r'^create/document/(?P<path>.*)$', 'createdoc', name='filebrowser_createdoc'),
    url(ur'^view/document/(?P<doc_slug>[-ÑñáéíóúÁÉÍÓÚ\w]+)/$', 'viewdoc', name='filebrowser_viewdoc'),
    url(ur'^edit/document/(?P<doc_slug>[-ÑñáéíóúÁÉÍÓÚ\w]+)/$', 'editdoc', name='filebrowser_editdoc'),
    url(r'^remove/(?P<type>[-\w]+)/attachment/(?P<objId>[-\w]+)/$', 'remove_attachment', name='filebrowser_remove_attachment'),
)
