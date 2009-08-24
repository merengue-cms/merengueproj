from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

# place app url patterns here
urlpatterns = patterns('merengue.multimedia.views',
#    url(r'^videos/(?P<video_id>[\w-]+)/(?P<width>\d+)x(?P<height>\d+)/video.xml$', 'video_xml', name='video_xml'),
    url(r'^videos/(?P<video_id>[\w-]+)/video.xml$', 'video_xml', name='video_xml'),
)
