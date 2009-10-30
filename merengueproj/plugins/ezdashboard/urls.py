from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('plugins.ezdashboard.views',
    url(r'^$', 'dashboard', name='dashboard'),
)
