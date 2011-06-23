(function($) {

    $(document).ready(function () {
        // Generic function //
        // Set a mark on a map (geomap) at the specified point
        function create_feature(geomap, point, name_map){

            var center = geomap.map.getCenter();
            var lonlat = new OpenLayers.LonLat(point.x, point.y).transform(new OpenLayers.Projection("EPSG:4326"),
            geomap.map.projection);
            center.lon = lonlat.lon;
            center.lat = lonlat.lat;
            geomap.map.setCenter(center);
            geomap.deleteFeatures();

            var point = new OpenLayers.Geometry.Point(lonlat.lon, lonlat.lat).transform(
                        new OpenLayers.Projection("EPSG:27700"), geomap.map.projection);
            var pointFeature = new OpenLayers.Feature.Vector(point);
            var vectorLayer = null;
            if (geomap.map.layers.length > 1){
                var i= 0;
                while(i< geomap.map.layers.length && vectorLayer == null){
                    if(geomap.map.layers[i].name==" "+name_map || geomap.map.layers[i].name==name_map){
                        vectorLayer = geomap.map.layers[i];
                    }
                    else{
                            i++;
                    }
                }
            }
            if(vectorLayer == null)
                vectorLayer = new OpenLayers.Layer.Vector("My Geometry");
            vectorLayer.addFeatures([pointFeature]);
            geomap.map.addLayer(vectorLayer);
            return lonlat;
        }
        // Funcion Especifica //
        // Join address info
        function get_address(thisJQuery){
            var fieldset = thisJQuery.parent().parent().parent();
            var address = add_space(fieldset.find("div.address").find("input").val());
            var postal_code = add_space(fieldset.find("div.postal_code").find("input").val());
            return address + " " + postal_code
        }

        function add_space(val){
            if(val!=null && val != "")
            {
                val = val +" ";
            }
            return val;
        }

        // "Click to locate" event fires an ajax request to Google
        $(".ajax_geolocation").click(function (){
            $("#img_ajax_loader").fadeIn();
            var address = $("#id_input_ajax").val();
            var geocoder = new GClientGeocoder();
            if (geocoder) {
                geocoder.getLatLng(
                address,
                function(point) {
                    if (!point) {
                        $($(".main_location")[0]).addClass("errors");
                        var html_text = $($(".main_location")[0]).html();
                        var error = $('<ul id="error_location" class="errorlist"><li>No localizated</li></ul>');
                        error.insertBefore($($(".main_location")[0]))

                        $("#img_ajax_loader").fadeOut();
                    } else {
                        var lonlat = create_feature(geodjango_main_location, point, "main_location");
                        $("#id_main_location_latitude").val(point.y);
                        $("#id_main_location_longitude").val(point.x);
                        $("div.main_location").find("textarea").html("SRID=900913;POINT("+lonlat.lon+" "+lonlat.lat+")");
                        $($(".main_location")[0]).removeClass("errors");
                        $("#error_location").fadeOut();
                        $("#img_ajax_loader").fadeOut();
                    }
                }
                );
            }
        }
        );


    // Update address events
    $("div.address input, div.postal_code input").keyup(function (){
            var thisJQuery = $(this);
            var inputs_ajax =$(".input_ajax");
            for (var i=0; i<inputs_ajax.length; i++){
                $(inputs_ajax[i]).val(get_address($(inputs_ajax[i])));
            }
    });

    // OSMGeoAdminLatitudeLongitude //

    // Generic event to convert latitude and longitude from Google Maps into an OpenLayer point
    $(".change_latitude, .change_longitude").change(function (){
        var thisJQuery = $(this);
        if(thisJQuery.val()!=null && thisJQuery.val()!="")
        {
            var coordenade = "longitude";
            if (this.id.indexOf("latitude") != -1){
                var coordenade = "latitude";
            }
            var idTextArea = thisJQuery.attr("id");
            textAreaJQuery = thisJQuery.parent().parent().parent().find("textarea");
            var lonlatOld = {'lon':0, 'lat':0};
            if(textAreaJQuery.val()){
                var lonLat = textAreaJQuery.val().replace("POINT", "").replace("(","").replace(")","").replace("SRID=900913;","").trim();
                var textAreaLongitude = lonLat.split(' ')[0];
                var textAreaLatitude = lonLat.split(' ')[1];
                var lonlatOld = new OpenLayers.LonLat(textAreaLongitude, textAreaLatitude).transform(geodjango_main_location.map.projection, new OpenLayers.Projection("EPSG:4326"))
            }
            if (coordenade == "latitude"){
                var lonlat = new OpenLayers.LonLat(lonlatOld.lon, thisJQuery.val()).transform(new OpenLayers.Projection("EPSG:4326"), geodjango_main_location.map.projection);
            }
            else{
                var lonlat = new OpenLayers.LonLat(thisJQuery.val(), lonlatOld.lat).transform(new OpenLayers.Projection("EPSG:4326"), geodjango_main_location.map.projection);

            }
            textAreaJQuery.html("SRID=900913;POINT("+lonlat.lon+" "+lonlat.lat+")");

        }
    });

    // Generic event that places a mark
    $(".view_on_map").click(function(){
        var thisJQuery = $(this);

        var id_formset = this.id.split("-");

        var id = id_formset[(id_formset.length -1)];

        var idSplit = id.split("_");

        var name_map = idSplit[idSplit.length-2]+"_"+idSplit[idSplit.length-1];
        var map = eval("geodjango_"+name_map);
        var latitude = thisJQuery.parent().find(".change_latitude").val();
        var longitude = thisJQuery.parent().find(".change_longitude").val();
        create_feature(map, {'y':latitude, 'x':longitude}, name_map);

    });

    var inputs_ajax =$(".input_ajax");
    for (var i=0; i<inputs_ajax.length; i++){
        $(inputs_ajax[i]).val(get_address($(inputs_ajax[i])));
    }

})
})
(jQuery);
