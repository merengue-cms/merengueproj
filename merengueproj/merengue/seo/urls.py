from django.conf.urls.defaults import patterns
from merengue.urlresolvers import merengue_url as url


urlpatterns = patterns('merengue.seo.views',
    url(r'^(?:/portal_links/(?P<with_portal_links>[0:1])/)?'
          r'(?:/menu_portal/(?P<with_menu_portal>[0:1])/)?'
          r'(?:/sections/(?P<with_sections>[0:1])/)?'
          r'(?:/menu_section/(?P<with_menu_section>[0:1])/)?'
          r'(?:/contents/(?P<with_contents>[0:1])/)?'
          r'sitemap.xml$', 'sitemap', name='sitemap'),
)
