(function($) {
    $.fn.inplaceeditform = function (opts, callback) {
        var defaults = {"getFieldUrl": "/implaceeditform/get_field/",
            "saveURL": "/inplaceeditform/save/",
            "successText": "Successfully saved"};
        var enabled = true;
        opts = $.extend(defaults, opts || {});
        this.each(function () {
            $(this).click(function() {
                if(!enabled) {
                    return true;
                }
                return false;
            });

            $(this).mouseenter(function() {
                if(!enabled) {
                    return false;
                }
                $(this).addClass("edit_over");
            });

            $(this).mouseleave(function() {
                $(this).removeClass("edit_over");
            });

            $(this).dblclick(function () {
                if(!enabled) {
                    return false;
                }
                $(this).data("inplace_enabled")
                var data = getDataToRequest($(this).find("span.config"));
                data += "&__widget_height=" + $(this).height() + "px" + "&__widget_width=" + $(this).width() + "px";
                var _this = $(this);
                $.ajax({
                data: data,
                url: opts.getFieldUrl,
                type: "GET",
                async:true,
                dataType: 'json',
                success: function(response) {
                    if (response == null) {
                        alert("The server is down");
                    }
                    else if (response.errors) {
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
                form.animate({opacity: 0.1});
                form.find("ul.errors").fadeOut(function(){$(this).remove();});
                var inplaceedit_conf = form.prev().find("span.config");
                var data = getDataToRequest(inplaceedit_conf);
                var field_id = form.find("span.field_id").html();
                var get_value = $(this).data("get_value"); // A hook
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
                url:  opts.saveURL,
                type: "POST",
                async: true,
                dataType: 'json',
                success: function(response){
                    if (response == null) {
                        alert("The server is down");
                    }
                    else if (response.errors) {
                        form.animate({opacity: 1});
                        form.prepend("<ul class='errors'><li>" + response.errors + "</li></ul>");
                    }
                    else {
                        _this.parent().fadeOut();
                        _this.fadeIn();
                        form.removeClass("inplaceeditformsaving");
                        var inplace_span = inplaceedit_conf.parents(".inplaceedit");
                        var config = inplace_span.find("span.config").html();
                        inplace_span.html(response.value + "<span class='config' style='display:none;'>" + config + "</span>");
                        var success_message = $("<ul class='success'><li>" + opts.successText + "</li></ul>")
                        inplace_span.prepend(success_message);
                        setTimeout(function(){
                            success_message.fadeOut(function(){
                                $(this).remove();
                            });
                        }, 2000);
                        inplace_span.show();
                        _this.parent().remove();
                    }
                }});
                return false;
            }

            function getDataToRequest(inplaceedit_conf) {
                var dataToRequest = "";
                var settings = inplaceedit_conf.find("span");
                $.map(settings, function (setting, i) {
                    var setting = $(setting);
                    var data = "&";
                    if (i == 0) {
                        data = "";
                    }
                    var key = setting.attr("class");
                    var value = setting.html();
                    data = data + key + "=" + value;
                    dataToRequest += data;
                });
                return dataToRequest;
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
    return {
        enable: function () {
            enabled = true;
        },
        disable: function () {
            enabled = false;
        }
    };
 }
})(jQuery);
