from django.conf.urls.defaults import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('merengue.base.views',
    (r'^admin_redirect/(?P<content_type>\d+)/(?P<content_id>\d+)/(?P<url>.*)$', 'admin_link'),
    (r'^public_redirect/(?P<app_label>\w+)/(?P<model_name>\w+)/(?P<content_id>\d+)/$', 'public_link'),
    url(r'^enviar_comentario/(?P<content_type>\d+)/(?P<content_id>\d+)/(?P<parent_id>\d+)/$',
        'content_comment_add', name='content_comment_add_parent'),
    url(r'^enviar_comentario/(?P<content_type>\d+)/(?P<content_id>\d+)/$', 'content_comment_add', name='content_comment_add'),
    url(r'^change_comment_visiblity/(?P<comment_id>\d+)/$', 'content_comment_change_visibity', name='content_comment_change_visibity'),
    url(r'^content_comment_delete/(?P<comment_id>\d+)/$', 'content_comment_delete', name='content_comment_delete'),
)
