{% extends "gis/admin/openlayers.js" %}
{% block base_layer %}new OpenLayers.Layer.Google("Google Base Layer", {'type': G_NORMAL_MAP, 'sphericalMercator' : true});{% endblock %}

{% block extra_layers %}
    {{ module }}.layers.satellite = new OpenLayers.Layer.Google( "Google Satellite", {type: G_SATELLITE_MAP, 'sphericalMercator': true} );
    {{ module }}.map.addLayer({{ module }}.layers.satellite);
{% endblock %}
