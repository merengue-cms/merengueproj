from django.conf.urls.defaults import patterns, url

SLUG_RE = r'[-_\w]+'

urlpatterns = patterns('plugins.ezdashboard.views',
    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^catalog/$', 'gadgets_list', name='catalog'),
    url(r'^meta/(?P<gadget_name>%s)/$' % SLUG_RE, 'gadget_meta',
        name='meta'),
    url(r'^content/(?P<gadget_name>%s)/$' % SLUG_RE, 'gadget_view',
        name='content'),
)
