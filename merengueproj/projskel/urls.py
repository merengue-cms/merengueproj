# don't touch this "import *" is necesary for urlresolvers works
from django.conf.urls.defaults import *
from django.conf import settings

from searchform.registry import search_form_registry
from admin import (setup_basecontents_admin,
                   setup_sections_admin, setup_multimedia_admin, setup_user_admin,
                   setup_extra_admin)

from merengue.base import admin

admin.autodiscover()


app_admin_sites = setup_basecontents_admin() + setup_sections_admin() + \
                  setup_multimedia_admin() + setup_user_admin()

# todos las subclases de basecontent tendran una interfaz de administracion
# especifica para tratar localizacion, informacion de contacto, multimedia,
# etc ...
app_admin_patterns = []
for model, app_admin_site, prefix in app_admin_sites:
    app_label = model._meta.app_label
    module_name = model._meta.module_name
    app_admin_patterns.append(
        (r'^admin/%s/%s/(?P<basecontent_id>\d+)/%s/(?P<url>.*)' %\
        (app_label, module_name, prefix), app_admin_site.root))


# do autodiscovering of all search forms
search_form_registry.autodiscover()

urlpatterns = patterns('', *app_admin_patterns)

js_info_dict = {
        'packages': ('django.conf', ),
}

urlpatterns += patterns('',
    (r'^admin/r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
     'cmsutils.views.generic.redirect_to_object'),
    (r'^admin/', admin.site.urls),
    # the next admin is only used for having the reverse url running
    # for 'admin'
    url(r'^admin/$', lambda request: '', name="admin_index"),

    url(r'^searchform/jsi18n/$', 'merengue.portal.views.searchform_jsi18n', name='searchform_jsi18n'),

    (r'^media/(.*)$', 'merengue.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    (r'^i18n/setlang/$', 'merengue.portal.views.set_language'),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^inplaceeditform/', include('inplaceeditform.urls')),

    # actions
    (r'^actions/', include('merengue.action.urls')),

    # login and logout
    url(r'^account/login/$', 'merengue.portal.views.try_login', name='login_form'),
    url(r'^account/logout/$', 'merengue.portal.views.logout', name='logout'),

    # base urls
    (r'^base/', include('merengue.base.urls')),

    (r'^ajax/autocomplete/tags/(?P<app_name>.*)/(?P<model>.*)/$',
     'merengue.portal.views.ajax_autocomplete_tags'),
    (r'^multimedia/', include('merengue.multimedia.urls')),
    # section
    (r'^sections/', include('merengue.section.urls')),
    # tinyimages
    (r'^tinyimages/', include('tinyimages.urls')),
    # other URLs
    (r'^internal-links/', include('merengue.internallinks.urls')),
    (r'^threadedcomments/', include('threadedcomments.urls')),
    url(r'^invalidate/$', 'merengue.portal.views.invalidate_cache', name='invalidate_cache'),
    # i18n applications
    url(r'^rosetta/', include('rosetta.urls')),
    url(r'^inlinetrans/', include('inlinetrans.urls')),

    # Your project URLs. Put here all your URLS:
    (r'^$', 'website.views.index'),
)
