(function($) {
    $.fn.inplaceeditform = function (o, callback) {
        var defaults = {"getFieldUrl": "/implaceeditform/get_field/",
            "saveURL": "/inplaceeditform/save/"}
        o = $.extend(defaults, o || {});
        return this.each(function () {
            $(this).click(function() {
                return false;
            });

            $(this).mouseenter(function() {
                $(this).addClass("edit_over");
            });

            $(this).mouseleave(function() {
                $(this).removeClass("edit_over");
            });

            $(this).dblclick(function () {
                var data = getDataToRequest($(this).find("span.config"));
                data += "&height=" + $(this).height() + "px" + "&width=" + $(this).width() + "px";
                var _this = $(this);
                $.ajax({
                data: data,
                url: o.getFieldUrl,
                type: "GET",
                async:true,
                dataType: 'json',
                success: function(response) {
                    if (response.errors) {
                        alert(response.errors);
                    }
                    else {
                        _this.hide();
                        var head = $("head")[0];
                        try {
                            var medias = $(response.field_media_render);
                            $.map(medias, function(media){
                               loadjscssfile(media);
                            });
                        }catch(err){
                        }
                        var tags = $(response.field_render);
                        $.map(tags, function(tag){
                            if (tag.tagName == "SCRIPT" || tag.tagName == "LINK") {
                                loadjscssfile(tag);
                            }
                        });
                        $(response.field_render).insertAfter(_this);
                        if(_this.next().parents("a").length > 0){
                            _this.next().click(function(){return false;});
                        }
                        _this.next().find(".cancel").click(inplaceCancel);
                        _this.next().find(".apply").click(inplaceApply);
                    }
                }});
            });

            function inplaceCancel() {
                $(this).parent().prev().fadeIn();
                $(this).parent().remove();
                return false;
            }

            function inplaceApply() {
                var form = $(this).parents("form.inplaceeditform");
                var inplaceedit_conf = form.prev().find("span.config");
                var data = getDataToRequest(inplaceedit_conf);
                var field_id = form.find("span.field_id").html();
                var get_value = $(this).data("get_value");
                if (get_value != null) {
                   var value = get_value(form, field_id);
                }
                else {
                    var value = form.find("#"+field_id).val();
                }
                data += "&value=" + encodeURIComponent($.toJSON(value));
                var _this = $(this);

                $.ajax({
                data: data,
                url:  o.saveURL,
                type: "POST",
                async: true,
                dataType: 'json',
                success: function(response){
                    if (response.errors) {
                        alert(response.errors);
                    }
                    else {
                        var inplace_span = inplaceedit_conf.parent();
                        var config = inplace_span.find("span.config").html();
                        inplace_span.html(response.value + "<span class='config'>" + config + "</span>");
                        inplace_span.show();
                        _this.parent().remove();
                    }
                }});

                $(this).parent().fadeOut();
                $(this).fadeIn();
                return false;
            }

            function getDataToRequest(inplaceedit_conf) {
                var field_name = inplaceedit_conf.find("span.field_name").html();
                var obj_id = inplaceedit_conf.find("span.obj_id").html();
                var content_type_id = inplaceedit_conf.find("span.content_type_id").html();
                var class_inplace = inplaceedit_conf.find("span.class_inplace").html();
                var filters_to_show = $.evalJSON(inplaceedit_conf.find("span.filters_to_show").html());
                var filters_to_edit = $.evalJSON(inplaceedit_conf.find("span.filters_to_edit").html());
                var adaptor = inplaceedit_conf.find("span.adaptor").html();
                var loads_tags = inplaceedit_conf.find("span.loads_tags").html();
                return ("field_name=" + field_name + "&obj_id="+ obj_id + "&content_type_id="
                        + content_type_id + "&filters_to_show="+ $.toJSON(filters_to_show)
                        + "&filters_to_edit="+ $.toJSON(filters_to_edit)
                        + "&field_adaptor=" + adaptor + "&class_inplace=" + class_inplace
                        + "$loads_tags=" + loads_tags);
            }

            function loadjscssfile(media){
                if (media.tagName=="SCRIPT"){ //if filename is a external JavaScript file
                    var fileref = document.createElement('script');
                    fileref.setAttribute("type","text/javascript");
                    fileref.setAttribute("id", media.id);
                    if(media.src != null && media.src != "" ){
                        fileref.setAttribute("src", media.src.replace("http://localhost:8000", ""));
                    } else {
                        fileref.innerHTML = media.innerHTML;
                    }
                }
                else if (media.tagName=="LINK" && media.type == "text/css"){ //if filename is an external CSS file
                    var fileref=document.createElement("link");
                    fileref.setAttribute("rel", "stylesheet");
                    fileref.setAttribute("type", "text/css");
                    fileref.setAttribute("href", media.href);
                }
                if (typeof fileref!="undefined") {
                    document.getElementsByTagName("head")[0].appendChild(fileref)
                }
            }
            });

            };
})(jQuery);
