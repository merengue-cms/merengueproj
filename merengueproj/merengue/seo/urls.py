from django.conf.urls.defaults import patterns
from merengue.urlresolvers import merengue_url as url

'''
Example urls ::

    /cms/seo/sitemap.xml
    /cms/seo/portal_links/1/sitemap.xml
    /cms/seo/menu_portal/1/sitemap.xml
    /cms/seo/sections/1/contents/1/sitemap.xml
    /cms/seo/portal_links/1/sections/1/contents/1/sitemap.xml
    /cms/seo/portal_links/0/menu_portal/0/sections/1/contents/1/sitemap.xml
'''

urlpatterns = patterns('merengue.seo.views',
    url(r'^(?:portal_links/(?P<with_portal_links>[0:1])/)?'
          r'(?:menu_portal/(?P<with_menu_portal>[0:1])/)?'
          r'(?:sections/(?P<with_sections>[0:1])/)?'
          r'(?:menu_section/(?P<with_menu_section>[0:1])/)?'
          r'(?:contents/(?P<with_contents>[0:1])/)?'
          r'sitemap.xml$', 'sitemap', name='sitemap'),
)
