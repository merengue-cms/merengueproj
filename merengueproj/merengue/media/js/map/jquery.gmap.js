// Google Maps API should be loaded before this
/*jslint bitwise: true, browser: true, eqeqeq: true, immed: true, newcap: true, nomen: true, plusplus: true, regexp: true, white: true, indent: 4, onevar: false */
/*global google, G_DEFAULT_ICON, G_GEO_UNKNOWN_ADDRESS, ClusterMarker, console, jQuery */
(function ($) {

    var debug = function (msg) {
        if (typeof console !== "undefined" && false ) { // remove '&& false' to get some debugging info
            console.debug(msg);
        }
    };

    // Aux functions
    var create_icon = function (url, width, height, anchor_x, anchor_y) {
        var icon = new google.maps.Icon(G_DEFAULT_ICON);
        icon.image = url;
        icon.shadow = '';
        icon.shadowSize = new google.maps.Size(0, 0);
        icon.iconSize = new google.maps.Size(width, height);
        icon.iconAnchor = new google.maps.Point(anchor_x, anchor_y);
        icon.imageMap = [0,0,width,0,width,height,0,height];
        return icon;
    };

    // Private function used by get_point_from_html_element and get_point_from_xml_element
    var set_point_defaults = function (point) {
        point.icon_width = point.icon_width ? parseInt(point.icon_width, 10): 24;
        point.icon_height = point.icon_height ? parseInt(point.icon_height, 10): 24;
        point.icon_anchor_x = point.icon_anchor_x ? parseInt(point.icon_anchor_x, 10): 12;
        point.icon_anchor_y = point.icon_anchor_y ? parseInt(point.icon_anchor_y, 10): 12;
        point.show_single = point.show_single ? parseInt(point.show_single, 10): 0;
    };

    var get_point_from_html_element = function (index, element) {
        var point = {
            id: parseInt($(".id", element).html(), 10),
            url: $(".url", element).html(),
            title: $(".title", element).html(),
            latitude: parseFloat($(".latitude", element).html()),
            longitude: parseFloat($(".longitude", element).html()),
            icon_image: $(".iconImage", element).html(),
            cluster_text: $(".clusterText", element).html(),
            cluster_icon_name: $(".clusterIcon", element).html(),
            // these are optional fields
            icon_width: $(".iconWidth", element).html(),
            icon_height: $(".iconHeight", element).html(),
            icon_anchor_x: $(".iconAnchorX", element).html(),
            icon_anchor_y: $(".iconAnchorY", element).html(),
            show_single: $(".showSingle", element).html()
        };
        set_point_defaults(point);
        return point;
    };

    var get_point_from_xml_element = function (element) {
        var point = {
            id: parseInt(element.getAttribute("id"), 10),
            url: element.getAttribute("path"),
            title: element.getAttribute("title"),
            latitude: parseFloat(element.getAttribute("lat")),
            longitude: parseFloat(element.getAttribute("lng")),
            icon_image: element.getAttribute("icon"),
            cluster_text: element.getAttribute("cluster_text"),
            cluster_icon_name: element.getAttribute("cluster_icon_name"),
            // these are optional fields
            icon_width: element.getAttribute("icon_width"),
            icon_height: element.getAttribute("icon_height"),
            icon_anchor_x: element.getAttribute("icon_anchor_x"),
            icon_anchor_y: element.getAttribute("icon_anchor_y")
        };
        set_point_defaults(point);
        return point;
    };

    var read_parameters = function (element) {
        var b0 = $(".mapParameters .bound0", element).html(),
            b1 = $(".mapParameters .bound1", element).html(),
            b2 = $(".mapParameters .bound2", element).html(),
            b3 = $(".mapParameters .bound3", element).html(),
            lat = $(".mapParameters .latitude", element).html(),
            lon = $(".mapParameters .longitude", element).html();
        return {
            bounds: [b0, b1, b2, b3],
            has_bounds: b0 !== null && b1 !== null && b2 !== null && b3 !== null,
            latitude: lat,
            longitude: lon,
            has_center: lat !== null && lon !== null,
            zoom: $(".mapParameters .zoom", element).html(),
            markers_url: $(".mapParameters .markersUrl", element).html(),
            show_areas: $(".mapParameters .showAreas", element).html(),
            markers_shown_initially: $(".mapParameters .markersShownInitially", element).html(),
            initial_points: $(".mapPoint", element).map(get_point_from_html_element)
        };
    };

    var read_panorama_parameters = function (element) {
        var has_panorama = $(".panoramaParameters .has_panorama", element).html();
        var yaw = $(".panoramaParameters .panorama_yaw", element).html();
        var pitch = $(".panoramaParameters .panorama_pitch", element).html();
        var panozoom = $(".panoramaParameters .panorama_zoom", element).html();
        return {
           lat: $(".panoramaParameters .panorama_lat", element).html(),
           lng: $(".panoramaParameters .panorama_lng", element).html(),
           yaw: yaw,
           pitch: pitch,
           panozoom: panozoom,
           get_nearest: yaw === null || pitch === null || panozoom === null,
           has_panorama: has_panorama !== null
        }
    };

    var read_map_messages = function (element) {
        return {
           directions_unknown_address_error: $('.googlemap-messages .directions_unknown_address_error', element).text(),
           directions_generic_error: $('.googlemap-messages .directions_generic_error', element).text()
        }
    };

    $.fn.gmap = function (options) {

        var opts = $.extend({}, $.fn.gmap.defaults, options);
        return this.each(function () {
                // initialize state
                var self = this;
                var map = null;
                var cluster = {};
                var markers = {};
                var latlngmarkers = {};
                var plus_icon = create_icon(opts.plus_icon_image, 12, 12, -2, -2);
                var params = read_parameters(this);
                var panorama_params = read_panorama_parameters(this);
                var messages = read_map_messages(this);

                var add_poligon_info = function (points) {
                    var point=[];
                    for (var i = 0; i < points.length; i++) {
                        var latitude = parseFloat(points[i].getAttribute("lat"));
                        var longitude = parseFloat(points[i].getAttribute("lng"));
                        point.push(new google.maps.LatLng(latitude, longitude));
                    }
                    poligon=new google.maps.Polygon(point, '#00ff00', 0, 0,'#00ff00',0.2);
                    map.addOverlay(poligon);
                }

                // Private functions
                var add_point_info = function (point, show) {
                    var latlng = new google.maps.LatLng(point.latitude, point.longitude);
                    var content_icon = create_icon(point.icon_image,
                                                   point.icon_width, point.icon_height,
                                                   point.icon_anchor_x, point.icon_anchor_y);
                    debug("adding point at " + latlng +
                          " " + point.icon_width + " " + point.icon_height +
                          " " + point.icon_anchor_x + " " + point.icon_anchor_y);

                    var marker = new google.maps.Marker(latlng, { icon: content_icon, title: point.title });
                    marker.cluster_text = point.cluster_text;
                    marker.cluster_icon_name = point.cluster_icon_name;
                    google.maps.Event.addListener(marker, "click", function (p) {
                            map.panTo(p);
                            if (point.url) {
                                url = point.url
                                if (point.show_single || opts.force_cluster_in_max_zoom) {
                                        url = (url.indexOf('?') < 0) ? url + '?' : url + '&';
                                        url = url + 'show_single=1';
                                }
                                google.maps.DownloadUrl(url, function (doc) {
                                        // Split the doc into pieces so we can create tabs
                                        var parts = $.trim(doc).split(/<div class="merengueContentInfo"/g);
                                        var tabs = [];
                                        var counter = 1;
                                        var max_height = 120;
                                        for (var i = 0; i < parts.length; i += 1) {
                                            var text = parts[i];
                                            if (text !== "") {
                                                text = '<div class="merengueContentInfo"' + text;
                                                tabs.push(new google.maps.InfoWindowTab("" + counter, text));
                                                counter += 1;
                                                start = text.indexOf('infoWindowHeight');
                                                if (start >= 0) {
                                                   start = text.indexOf('>', start) + 1;
                                                   end = text.indexOf('</span>', start);
                                                   height = text.substring(start, end);
                                                   max_height = Math.max(max_height, parseInt(height, 10));
                                                }
                                            }
                                        }
                                        // Don't use marker.openInfoWindowTabs because
                                        // we can't set the size properly
                                        var new_size = new google.maps.Size(Math.max(70 * counter, 200), max_height);
                                        map.getInfoWindow().reset(marker.getLatLng(), tabs, new_size);
                                        map.panBy(new google.maps.Size(0, 90));
                                    });
                            }
                        });

                    // add the marker
                    markers[point.id] = marker;
                    if (show) {
                        // show the marker
                        show_marker(marker);
                    }

                    return marker;
                };

                var create_cluster = function(cluster_icon_name, cluster_text) {
                    var cluster_icon = create_icon(cluster_icon_name, 24, 24, 10, 35);
                    return new ClusterMarker(map, {clusterMarkerIcon: cluster_icon,
                                                   clusterMarkerTitle: cluster_text,
                                                   forceClusterInMaxZoom: opts.force_cluster_in_max_zoom,
                                                   clusteringEnabled: opts.clustering_enabled});
                }

                var show_marker = function(marker) {
                    // private function that shows a marker previously added
                    var already_in_map = false;
                    if (latlngmarkers[marker.getPoint().toUrlValue()]) {
                        already_in_map = true;
                    }
                    if (already_in_map && !opts.force_cluster_in_max_zoom) {
                        if (typeof cluster[marker.cluster_icon_name] == "undefined") {
                            cluster[marker.cluster_icon_name] = create_cluster(marker.cluster_icon_name, marker.cluster_text);
                        }
                        cluster[marker.cluster_icon_name].addMarkers([new google.maps.Marker(marker.getPoint(), {icon: plus_icon, clickable: false})]);
                    } else {
                        if (typeof cluster[marker.cluster_icon_name] == "undefined") {
                            cluster[marker.cluster_icon_name] = create_cluster(marker.cluster_icon_name, marker.cluster_text);
                        }
                        cluster[marker.cluster_icon_name].addMarkers([marker]);
                    }
                    if (!latlngmarkers[marker.getPoint().toUrlValue()]) {
                        latlngmarkers[marker.getPoint().toUrlValue()] = true;
                    }
                };

                $(this).bind("show-all-markers", function () {
                    // an event that you can trigger if you wants to show all markers
                    for (var id in markers) {
                        show_marker(markers[id]);
                    }
                    for (var id in cluster) {
                        cluster[id].refresh();
                    }
                });

                $(this).bind("hide-all-markers", function () {
                    // an event that you can trigger if you wants to hide all markers
                    for (var id in markers) {
                        marker = markers[id];
                        latlngmarkers[marker.getPoint().toUrlValue()] = false;
                    }
                    for (var id in cluster) {
                        cluster[id].removeMarkers();
                        cluster[id].refresh();
                    }
                });

                var filter_markers = null;
                var bounds = null;

                var zoom = params.zoom === null ? opts.zoom : parseInt(params.zoom, 10);
                var show_markers = false;

                // Initialize the map

                map = new google.maps.Map2(this);
                $(this).data("map", map);

                if (panorama_params.has_panorama) {
                    var showPanoData = function(panoData) {
                        if (panoData.code != 200) {
                            $(opts.panorama_slide_trigger).hide().trigger('full-hide');
                            return;
                        }
                        $(opts.panorama_slide_trigger).show().trigger('full-show');
                    }

                    if (panorama_params.get_nearest) {
                        var panorama_client = new google.maps.StreetviewClient();
                        var panorama_location = new google.maps.LatLng(panorama_params.lat,panorama_params.lng);
                        panorama_client.getNearestPanorama(panorama_location, showPanoData);
                    } else {
                        $(opts.panorama_slide_trigger).show().trigger('full-show');
                    }
                }

                if (params.has_bounds) {
                    bounds = new google.maps.LatLngBounds();
                    bounds.extend(new google.maps.LatLng(parseFloat(params.bounds[1]), parseFloat(params.bounds[0])));
                    bounds.extend(new google.maps.LatLng(parseFloat(params.bounds[3]), parseFloat(params.bounds[2])));
                    map.setCenter(bounds.getCenter(), map.getBoundsZoomLevel(bounds));
                } else if (params.has_center) {
                    var center = new google.maps.LatLng(parseFloat(params.latitude), parseFloat(params.longitude));
                    debug("setCenter " +  zoom);
                    map.setCenter(center, zoom);
                }

                if (params.markers_shown_initially) {
                    show_markers = true;
                }

                if (opts.map_type !== null) {
                    debug("setMapType " + opts.map_type);
                    map.setMapType(opts.map_type);
                }

                if (!opts.no_ui) {
                    if (opts.use_small_controls) {
                        debug("addControl");
                        map.addControl(new google.maps.SmallZoomControl3D());
                    } else {
                        debug("setUIToDefault");
                        map.setUIToDefault();
                    }
                }

                if (opts.enable_scroll_wheel_zoom) {
                    debug("enableScrollWheelZoom");
                    map.enableScrollWheelZoom();
                }

                // Bind optional events
                $(this).bind('openinmap', function (ev, data) {
                    debug("Received openinamp event");
                    if (typeof markers[data.point_id] !== "undefined") {
                        var mk = markers[data.point_id];
                        GEvent.trigger(mk, 'click', mk.getPoint());
                    }
                });

                // Add points to the map
                for (var i = 0; i < params.initial_points.length; i += 1) {
                    add_point_info(params.initial_points[i], show_markers);
                }

                for (var id in cluster) {
                    cluster[id].refresh();
                }

                if (params.markers_url) {
                    debug("Downloading markers url");
                    google.maps.DownloadUrl(params.markers_url, function (doc) {
                            var xmlDoc = google.maps.Xml.parse(doc);
                            var xml_markers = xmlDoc.documentElement.getElementsByTagName("marker");

                            for (var i = 0; i < xml_markers.length; i += 1) {
                                var point = get_point_from_xml_element(xml_markers[i]);
                                add_point_info(point, show_markers);
                            }

                            for (var id in cluster) {
                                cluster[id].refresh();
                            }

                            if (params.show_areas) {
                                var areas = xmlDoc.documentElement.getElementsByTagName("area");
                                for (var i = 0; i < areas.length; i += 1) {
                                    var poligons = areas[i].getElementsByTagName("poligon");
                                    for (var j = 0; j < poligons.length; j++) {
                                        var points = poligons[j].getElementsByTagName("point");
                                        add_poligon_info(points);
                                    }
                                }
                            }
                        });
                }

                // Optional features
                if (opts.show_directions) {
                    debug("Showing directions");
                    // Aux functions for directions
                    var show_howto_arrive = function () {
                        $(opts.directions_sidebar_selector).show();
                        $(self).width("500px");
                        if (map) {
                            map.checkResize();
                        }
                        return false; // to avoid execution of default handler
                    };

                    var hide_howto_arrive = function () {
                        $(opts.directions_sidebar_selector).hide();
                        $(self).width("775px");
                        if (map) {
                            map.checkResize();
                        }
                        return false; // to avoid execution of default handler
                    };

                    var gdir = new google.maps.Directions(map, $(opts.directions_area_selector)[0]);

                    google.maps.Event.addListener(gdir, "error", function () {
                            hide_howto_arrive();
                            if (gdir.getStatus().code === G_GEO_UNKNOWN_ADDRESS) {
                                alert(messages.directions_unknown_address_error);
                            } else {
                                alert(messages.directions_generic_error);
                            }
                        });
                    $(opts.directions_form_selector).show();
                    $(opts.directions_form_selector).find('form').submit(function () {
                            var from = $("input[type=text]", this).val();
                            from = from.replace(/\s+$/, ""); // rstrip
                            if (from.toLowerCase() === "granada") { // Google error workaround
                                from += ", spain";
                            }
                            $(opts.directions_area_selector).empty();
                            show_howto_arrive();

                            if (params.initial_points.length > 0) {
                                var first_point = params.initial_points[0];
                                gdir.loadFromWaypoints([from, new google.maps.LatLng(first_point.latitude, first_point.longitude)]);
                            } else if (params.has_bounds) {
                                gdir.loadFromWaypoints([from, bounds.getCenter()]);
                            } else {
                                gdir.loadFromWaypoints([from, map.getCenter()]);
                            }
                            return false;
                        });

                    $(opts.directions_sidebar_selector + " a.close-link").click(hide_howto_arrive);

                }

                if (opts.filters_selector) {
                    debug("Setup filters");

                    // Filter Markers functions
                    var update_markers = function (umodel, force, show_areas) {
                        var actual_zoom = map.getZoom();
                        if ((actual_zoom < filter_markers[umodel].zoom) || force || filter_markers[umodel].force_recalculate) {
                            var point1 = map.getBounds().getNorthEast();
                            var point2 = map.getBounds().getSouthWest();
                            if (filter_markers[umodel].cluster === null) {
                                // Initialize this cluster
                                var cluster_icon = create_icon(filter_markers[umodel].cluster_icon, 24, 24, 12, 12);
                                filter_markers[umodel].cluster = new ClusterMarker(map, {clusterMarkerIcon: cluster_icon,
                                                                                         clusterMarkerTitle: filter_markers[umodel].cluster_text,
                                                                                         forceClusterInMaxZoom: opts.force_cluster_in_max_zoom});
                            }

                            // Load the markers with ajax
                            var request_args = {
                                type: filter_markers[umodel].model,
                                related_type: opts.content_type_id,
                                related_id: opts.content_id,
                                lat1: point1.lat(),
                                lng1: point1.lng(),
                                lat2: point2.lat(),
                                lng2: point2.lng()
                            };
                            var filter_url = opts.filter_url;
                            if ($(opts.alternative_filter_url).length) {
                                filter_url = $(opts.alternative_filter_url).html();
                            }
                            $.get(filter_url + '?' + $.param(request_args), function (data) {
                                    var xmlDoc = google.maps.Xml.parse(data);
                                    var xml_markers = xmlDoc.documentElement.getElementsByTagName("marker");
                                    filter_markers[umodel].items = [];
                                    filter_markers[umodel].areas = [];
                                    for (var i = 0; i < xml_markers.length; i += 1) {
                                        var point = get_point_from_xml_element(xml_markers[i]);
                                        var point_info = add_point_info(point, false);
                                        filter_markers[umodel].items.push(point_info);
                                    }
                                    filter_markers[umodel].cluster.removeMarkers();
                                    if (filter_markers[umodel].items.length > 0) {
                                        filter_markers[umodel].cluster.addMarkers(filter_markers[umodel].items);
                                    }
                                    filter_markers[umodel].cluster.refresh();
                                    /*
                                    if (show_areas) {
                                        var areas = xmlDoc.documentElement.getElementsByTagName("area");
                                        for (var i = 0; i < areas.length; i += 1) {
                                            var poligons = areas[i].getElementsByTagName("poligon");
                                            for (var j = 0; j < poligons.length; j++) {
                                                var points = poligons[j].getElementsByTagName("point");
                                                filter_markers[umodel]['areas'].push(add_poligon_info(map, points));
                                            }
                                        }
                                    }
                                    */
                                    filter_markers[umodel].zoom = map.getZoom();
                                    setTimeout(function () {
                                            $(opts.progress_feedback_selector).hide("slow");
                                        }, 100);
                                });
                        } else {
                            /*
                            for (var i = 0; i < filter_markers[umodel]['areas'].length ; i += 1) {
                                filter_markers[umodel]['areas'][i].show();
                            }
                            */
                            filter_markers[umodel].cluster.removeMarkers();
                            if (filter_markers[umodel].items.length > 0) {
                                filter_markers[umodel].cluster.addMarkers(filter_markers[umodel].items);
                            }
                            filter_markers[umodel].cluster.refresh();
                            $(opts.progress_feedback_selector).hide("slow");
                        }
                        filter_markers[umodel].show = true;
                    }; // End of update markers

                    filter_markers = []; // this variable is defined above
                    $(opts.filters_selector).each(function () {
                            // Initialize filter markers
                            var model = $(this).val();
                            var underscore_model = model.replace(".", "_");
                            filter_markers[underscore_model] = {
                                items: [],
                                areas: [],
                                model: model,
                                zoom: 300,
                                force_recalculate: false,
                                cluster: null,
                                cluster_text: $(this).siblings(".clusterText").html(),
                                cluster_icon: $(this).siblings(".clusterIcon").html()
                            };

                        }).click(function () {
                                // Update the markers when clicking on a filter checkbox
                                var umodel = $(this).val().replace('.', '_');
                                if (!$(this).attr('checked')) {
                                    for (var i = 0; i < filter_markers[umodel].areas.length; i += 1) {
                                        filter_markers[umodel].areas[i].hide();
                                    }
                                    filter_markers[umodel].cluster.removeMarkers();
                                    filter_markers[umodel].cluster.refresh();
                                    filter_markers[umodel].show = false;
                                } else {
                                    $(opts.progress_feedback_selector).show("fast");

                                    var show_areas = $(this).hasClass('withbounds');
                                    setTimeout(function () {
                                            update_markers(umodel, false, show_areas);
                                        }, 500);
                                }
                            });


                    // Setup some google map events for filters
                    if (opts.recalculate_marks_when_map_changes) {
                        debug("Setup recalculate marks when map changes");
                        var set_force_recalculate = function () {
                            for (var i in filter_markers) {
                                if (filter_markers.hasOwnProperty(i)) {
                                    filter_markers[i].force_recalculate = true;
                                }
                            }
                        };
                        google.maps.Event.addListener(map, "zoomend", set_force_recalculate);
                        google.maps.Event.addListener(map, "moveend", set_force_recalculate);
                    }

                } // End of if related filters

	        var travelgdir = new google.maps.Directions(map, $(opts.directions_area_selector)[0]);
                google.maps.Event.addListener(travelgdir, "error", function () {
                        hide_howto_arrive();
                        if (travelgdir.getStatus().code === G_GEO_UNKNOWN_ADDRESS) {
                            alert(messages.directions_unknown_address_error);
                        } else {
                            alert(messages.directions_generic_error);
                        }
                    });

                $(".calculate-travel-route").each(function() {
                    var ajax_url = $(this).find('span.ajaxUrl').text();
                    $(this).find('a.trigger-link').click(function() {
		        $.ajax({
                            url: ajax_url,
                            dataType: 'json',
                            success: function (data) {
                                var sorted_ids = data;
                                var travelpoints = [];
                                var num_points = 0;
                                for (var i in sorted_ids) {
                                    if (typeof(markers[sorted_ids[i]]) != 'undefined') {
                                        travelpoints.push(
                                           markers[sorted_ids[i]].getTitle() +
                                           "@" + markers[sorted_ids[i]].getLatLng().toString() + "");
                                        num_points = num_points + 1;
                                        // Limited by google API
                                        if (num_points >= 25) break;
                                    }
                                }
                                if (num_points==1) {
                                   travelpoints.push(travelpoints[0]);
                                }
                                $(opts.directions_area_selector).empty();
                                show_howto_arrive();
		                travelgdir.loadFromWaypoints(travelpoints);
                            }
                        });
                        return false;
                    });
                });
            }); // End of each
        
    }; // End of map

    $.fn.gmap.defaults = {
        map_type: null,
        zoom: 5,
        enable_scroll_wheel_zoom: true,
        use_small_controls: false,
        plus_icon_image: "",
        show_directions: true,
        panorama_slide_trigger: ".toStreet",
        panorama_container_selector: ".panoramasection",
        panorama_id: "panorama",
        directions_form_selector: ".googlemap-directions-form",
        directions_area_selector: ".googlemap-directions",
        directions_sidebar_selector: ".googlemap-sidebar",
        colorify_areas: false,
        filters_selector: "div.mapFilters input.mapFilter",
        alternative_filter_url: "div.mapFilters span.filterurl",
        progress_feedback_selector: "span.progressFeedback",
        filter_url: null,
        content_type_id: null,
        content_id: null,
        force_cluster_in_max_zoom: false,
        recalculate_marks_when_map_changes: false
    };

}(jQuery));
