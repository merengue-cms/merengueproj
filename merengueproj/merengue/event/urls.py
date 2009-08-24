from django.conf.urls.defaults import patterns, url

from merengue.section.urls import docs_patterns, agenda_patterns

urlpatterns = patterns('merengue.event.views',
    url(r'^$', 'event_index', name='event_index'),
    url(r'^mas-votados/$', 'top_events_rated', name='event_top_rated'),
    url(r'^busqueda/$', 'event_search', name='event_search'),
    url(r'^busqueda/rapida/$', 'event_quick_search', name='event_quick_search'),
    url(r'^busqueda/avanzada/$', 'event_advanced_search', name='event_advanced_search'),
)

urlpatterns += agenda_patterns(section_slug='eventos',
                               name='event')

urlpatterns += patterns('event.views',
    url(r'^(?P<event_slug>[\w-]+)/$', 'event_view', name='event_view'),
)

urlpatterns += docs_patterns(section_slug='eventos',
                             name='event',
                             prefix='documentos/',
)
