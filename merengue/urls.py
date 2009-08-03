# don't touch this "import *" is necesary for urlresolvers works
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from searchform.registry import search_form_registry
from admin import (setup_basecontents_admin,
                   setup_sections_admin, setup_multimedia_admin, setup_user_admin,
                   setup_extra_admin)

admin.autodiscover()
app_admin_sites = setup_basecontents_admin() + setup_sections_admin() + \
                  setup_multimedia_admin() + setup_user_admin()
app_admin_sites_extra = setup_extra_admin()
app_admin_patterns = []

# todos las subclases de basecontent tendran una interfaz de administracion
# especifica para tratar localizacion, informacion de contacto, multimedia,
# etc ...
for model, app_admin_site, prefix in app_admin_sites:
    app_label = model._meta.app_label
    module_name = model._meta.module_name
    app_admin_patterns.append(
        (r'^admin/%s/%s/(?P<basecontent_id>\d+)/%s/(?P<url>.*)' %\
        (app_label, module_name, prefix), app_admin_site.root))


for model, app_admin_site, prefix in app_admin_sites_extra:
    app_admin_patterns.append(
        (r'^%s/(?P<url>.*)' % prefix, app_admin_site.root))

# do autodiscovering of all search forms
search_form_registry.autodiscover()

urlpatterns = patterns('',
    (r'^admin/pending_[\w]+/$', 'portal.views.list_pending_redirect'),
)

urlpatterns += patterns('', *app_admin_patterns)

js_info_dict = {
        'packages': ('django.conf', ),
}

urlpatterns += patterns('',
    (r'^admin/contenidos/pendientes/$', 'portal.views.list_pending'),
    (r'^admin/r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
     'cmsutils.views.generic.redirect_to_object'),
    (r'^admin/(.*)', admin.site.root),
    # the next admin is only used for having the reverse url running
    # for 'admin'
    url(r'^admin/$', lambda request: '', name="admin_index"),

    url(r'^searchform/jsi18n/$', 'portal.views.searchform_jsi18n', name='searchform_jsi18n'),

    (r'^media/(.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    (r'^cms/(.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT + '/cms'}),
    (r'^i18n/setlang/$', 'portal.views.set_language'),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^inplaceeditform/', include('inplaceeditform.urls')),
    (r'^$', 'portal.views.index'),

    # login and logout
    url(r'^cuentas/entrar/$', 'portal.views.try_login', name='login_form'),
    url(r'^cuentas/salir/$', 'portal.views.logout', name='logout'),
    url(r'^mapa-web/$', 'portal.views.site_map', name='site_map'),

    # base urls
    (r'^base/', include('base.urls')),
    url(r'^infraestructuras/(?P<feature_slug>.+)/$',
        'base.views.feature_listing', name='feature_listing'),

    (r'^ajax/autocomplete/tags/(?P<app_name>.*)/(?P<model>.*)/$',
     'portal.views.ajax_autocomplete_tags'),
    (r'^multimedia/', include('multimedia.urls')),
    # section
    (r'^secciones/', include('section.urls')),
    # tinyimages
    (r'^tinyimages/', include('tinyimages.urls')),
    # other URLs
    (r'^internal-links/', include('internallinks.urls')),
    (r'^threadedcomments/', include('threadedcomments.urls')),
    url(r'^invalidate/$', 'portal.views.invalidate_cache', name='invalidate_cache'),
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

if 'inlinetrans' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^inlinetrans/', include('inlinetrans.urls')),
    )
