from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('merengue.block.views',
    url(r'order/ajax/', 'blocks_reorder', name='blocks_reorder'),
)
