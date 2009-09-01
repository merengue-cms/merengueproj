(function($) {
    $(document).ready(function () {
            var google_files_are_loaded = false;

            function load_google_files(callback) {
                var api_key = $("span#google-maps-api-key").html();
                var script_url = "http://www.google.com/jsapi?key=" + api_key;
                $.getScript(script_url, function () {
                        google.load("maps", "2.x", {'callback': callback});
                    });
            };

            function show_map(map_node) {
                if (GBrowserIsCompatible()) {
                    var properties = map_node.children();
                    var longitude = parseFloat($(properties[0]).html());
                    var latitude = parseFloat($(properties[1]).html());
                    var icon = $(properties[2]).html();
                    var zoom = parseInt($(properties[3]).html());
                    var index = $(properties[4]).html();

                    var content_icon = new google.maps.Icon(G_DEFAULT_ICON);
                    content_icon.iconSize = new google.maps.Size(24, 24);
                    content_icon.iconAnchor = new google.maps.Point(12, 12);
                    content_icon.image = icon;
                    content_icon.shadow = '';
                    content_icon.shadowSize = new google.maps.Size(0,0);

                    var pos = new google.maps.LatLng(latitude, longitude);
                    map_node.fadeIn();
                    var map = new GMap2(map_node[0]);

                    map.setCenter(new GLatLng(latitude, longitude), zoom);

                    var thismarker = new google.maps.Marker(pos,{icon: content_icon});
                    google.maps.Event.addListener(thismarker, "click", function(p) {
                            map.panTo(p);
                        });

                    map.addControl(new google.maps.SmallMapControl());
                    map.addOverlay(thismarker);
                    map_node.fadeIn();
                }

            };

            $(".fadeingooglemap").click(function (){
                    var link = $(this);
                    var div_content = link.parent().prev();
                    link.parent().fadeOut();

                    if (!google_files_are_loaded) {
                        load_google_files(function () {
                                show_map(div_content);
                            });
                        google_files_are_loaded = true;
                    } else {
                        show_map(div_content);
                    }

                });
 
        });
})(jQuery);
