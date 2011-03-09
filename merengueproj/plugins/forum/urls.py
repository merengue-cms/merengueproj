from django.conf.urls.defaults import patterns
from merengue.urlresolvers import merengue_url as url


urlpatterns = patterns('plugins.forum.views',
    url(r'^$', 'forum_index', name='forum_index'),
    url({'en': r'^change_comment_visiblity/(?P<comment_id>\d+)/$',
         'es': r'^cambiar_visibilidad_del_comentario/(?P<comment_id>\d+)/$'},
         'forum_comment_change_visibity', name='forum_comment_change_visibity'),
    url({'en': r'^comment_delete/(?P<comment_id>\d+)/$',
         'es': r'^eliminar_comentario/(?P<comment_id>\d+)/$'},
         'forum_comment_delete', name='forum_comment_delete'),
    url({'en': r'^create_thread$',
         'es': r'^crear_hilo$'},
         'create_new_thread', name='create_new_thread'),
    url({'en': r'^add_comment/(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/(?P<parent_id>\d+)/$',
         'es': r'^anadir_comentario/(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/(?P<parent_id>\d+)/$'},
        'forum_comment_add', name='forum_child_comment_add'),
    url({'en': r'^add_comment/(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/$',
         'es': r'^anadir_comentario/(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/$'},
         'forum_comment_add', name='forum_comment_add'),
    url(r'^(?P<forum_slug>[\w-]+)/$', 'forum_view', name='forum_view'),
    url({'en': r'^(?P<forum_slug>[\w-]+)/create_thread$',
         'es': r'^(?P<forum_slug>[\w-]+)/crear_hilo$'},
         'create_new_thread', name='create_new_thread'),
    url(r'^(?P<forum_slug>[\w-]+)/(?P<thread_slug>[\w-]+)/$', 'thread_view', name='thread_view'),
)
