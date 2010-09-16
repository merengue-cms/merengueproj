# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.filebrowser.views',
    url(r'^(?P<repository_name>[\w-]+)/$', 'root', name='filebrowser_root'),
    url(r'^(?P<repository_name>[\w-]+)/listado/$', 'listing', name='filebrowser_root_listing'),
    url(r'^(?P<repository_name>[\w-]+)/listado/(?P<path>.*)$', 'listing', name="filebrowser_dir_listing"),
    url(r'^(?P<repository_name>[\w-]+)/descarga/(?P<path>.*)$', 'download', name='filebrowser_download'),
    url(r'^(?P<repository_name>[\w-]+)/subida/(?P<path>.*)$', 'upload', name='filebrowser_upload'),
    url(r'^(?P<repository_name>[\w-]+)/crear/directorio/(?P<path>.*)$', 'createdir', name='filebrowser_createdir'),
    url(r'^(?P<repository_name>[\w-]+)/accion/(?P<path>.*)$', 'action', name='filebrowser_action'),

    # documents
    url(r'^crear/documento/(?P<path>.*)$', 'createdoc', name='filebrowser_createdoc'),
    url(ur'^ver/documento/(?P<doc_slug>[-ÑñáéíóúÁÉÍÓÚ\w]+)/$', 'viewdoc', name='filebrowser_viewdoc'),
    url(ur'^editar/documento/(?P<doc_slug>[-ÑñáéíóúÁÉÍÓÚ\w]+)/$', 'editdoc', name='filebrowser_editdoc'),
    url(r'^borrar/(?P<type>[-\w]+)/adjunto_a/(?P<objId>[-\w]+)/$', 'remove_attachment', name='filebrowser_remove_attachment'),
)
