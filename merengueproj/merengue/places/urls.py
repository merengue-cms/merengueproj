from django.conf.urls.defaults import patterns, url

from merengue.section.urls import section_patterns

urlpatterns = patterns('places.views',
    url(r'^$', 'places_index', name='places_index'),
    url(r'^busqueda/$', 'places_search', name='places_search'),
    url(r'^busqueda/rapida/$', 'places_quick_search', name='places_quick_search'),
    url(r'^busqueda/avanzada/$', 'places_advanced_search', name='places_advanced_search'),
    url(r'^ajax/provincia/$', 'places_ajax_province', name='places_ajax_province'),
    url(r'^ajax/provincia/coast/$', 'places_ajax_province_coast', name='places_ajax_province_coast'),
    url(r'^ajax/zona_turistica/$', 'places_ajax_tourist_zone', name='places_ajax_tourist_zone'),
    url(r'^ajax/municipio/$', 'places_ajax_city', name='places_ajax_city'),
    url(r'^ajax/nearby/$', 'places_ajax_nearby', name='places_ajax_nearby'),
    url(r'^ajax/related/$', 'places_ajax_related', name='places_ajax_related'),
    url(r'^ajax/resources_map/(?P<place_type>[\w-]+)/(?P<place_id>[\d]+)/(?P<class_name>\w+)/$', 'places_ajax_resources_map', name='places_ajax_resources_map'),

    # provinces
    url(r'^provincias/(?P<province_slug>[\w-]+)/$', 'province_view', name='province_view'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/mapa/$', 'province_map_view', name='province_map_view'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/recurso/(?P<class_name>\w+)/$', 'province_resource_view', name='province_resource_view'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/busqueda/$', 'province_search_view', name='province_search_view'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/busqueda/rapida/$', 'province_quick_search', name='province_quick_search'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/busqueda/avanzada/$', 'province_advanced_search', name='province_advanced_search'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/municipios/$', 'province_cities', name='province_cities'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/multimedia/$', 'province_multimedia', name='province_multimedia'),

    # tourist zones
    url(r'^zonasturisticas/(?P<touristzone_slug>[\w-]+)/$', 'touristzone_view', name='touristzone_view'),
    url(r'^zonasturisticas/(?P<touristzone_slug>[\w-]+)/mapa/$', 'touristzone_map_view', name='touristzone_map_view'),
    url(r'^zonasturisticas/(?P<touristzone_slug>[\w-]+)/recurso/(?P<class_name>\w+)/$', 'touristzone_resource_view', name='touristzone_resource_view'),
    url(r'^zonasturisticas/(?P<touristzone_slug>[\w-]+)/busqueda/$', 'touristzone_search_view', name='touristzone_search_view'),
    url(r'^zonasturisticas/(?P<touristzone_slug>[\w-]+)/busqueda/rapida/$', 'touristzone_quick_search', name='touristzone_quick_search'),
    url(r'^zonasturisticas/(?P<touristzone_slug>[\w-]+)/busqueda/avanzada/$', 'touristzone_advanced_search', name='touristzone_advanced_search'),
    url(r'^zonasturisticas/(?P<touristzone_slug>[\w-]+)/municipios/$', 'touristzone_cities', name='touristzone_cities'),
    url(r'^zonasturisticas/(?P<touristzone_slug>[\w-]+)/multimedia/$', 'touristzone_multimedia', name='touristzone_multimedia'),

    # cities
    url(r'^provincias/(?P<province_slug>[\w-]+)/municipios/(?P<city_slug>[\w-]+)/$', 'city_view', name='city_view'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/municipios/(?P<city_slug>[\w-]+)/villages/$', 'city_villages', name='city_villages'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/municipios/(?P<city_slug>[\w-]+)/mapa/$', 'city_map_view', name='city_map_view'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/municipios/(?P<city_slug>[\w-]+)/recurso/(?P<class_name>\w+)/$', 'city_resource_view', name='city_resource_view'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/municipios/(?P<city_slug>[\w-]+)/multimedia/$', 'city_multimedia', name='city_multimedia'),
    url(r'^provincias/(?P<province_slug>[\w-]+)/municipios/(?P<city_slug>[\w-]+)/historia/$', 'city_history', name='city_history'),

    url(r'^andalucia_content_info/(?P<content_type>\d+)/(?P<content_id>\d+)/$', 'content_info', name='content_info'),
    url(r'^location_redirect/(?P<plone_uid>\w+)/(?P<location_model>\w+)$', 'location_redirect'),
)

urlpatterns += section_patterns(section_slug='destinos',
                             name='places',
)
