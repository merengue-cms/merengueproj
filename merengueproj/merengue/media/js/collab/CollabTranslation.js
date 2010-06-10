(function ($) {
    $.fn.CollaborativeTranslation = function () {
        return this.each(function () {
            var trigger_link = $(this);
            var main_ui = null;
            var outer_zone = null;
            var translation_zone = null;
            var is_html = null;
 
            var initTrigger = function() {
                trigger_link.click(initCollaborativeTranslation);
            }

            var boundTranslationForm = function() {
                translation_zone.find('#collab-translation-edit-form').ajaxForm({
                    beforeSerialize: function(form, options) {
                        textarea_id = translation_zone.find('textarea').attr('id');
                        if (typeof(textarea_id)!='undefined')
                            tinyMCE.get(textarea_id).save();
                    },
                    success: function(response, status) {
                        if (is_html) {
                            textarea_id = translation_zone.find('textarea').attr('id');
                            if (typeof(textarea_id)!='undefined')
                                tinyMCE.execCommand('mceRemoveControl', false, textarea_id);
                        }
                        translation_zone.html(response);
                        boundTranslationForm();
                    }
                });
                translation_zone.find('select').change(function() {
                    var lang = $(this).val();
                    var href = translation_zone.find('.collab-translation-edit-form-url-for-'+lang).text();
                    setTranslationZone(href);
                });
                if (is_html) {
                    textarea_id = translation_zone.find('textarea').attr('id');
                    if (typeof(textarea_id)!='undefined')
                        tinyMCE.execCommand('mceAddControl', false, textarea_id);
                }
            }

            var setTranslationZone = function(href) {
                $.ajax({
                    url: href,
                    type: "GET",
                    async: true,
                    success: function(response){
                        if (is_html) {
                            textarea_id = translation_zone.find('textarea').attr('id');
                            if (typeof(textarea_id)!='undefined')
                                tinyMCE.execCommand('mceRemoveControl', false, textarea_id);
                        }
                        translation_zone.html(response).show();
                        boundTranslationForm();
                    }});
                return false;
            }

            var setCollaborativeTranslationActions = function() {
                outer_zone.click(closeCollaborativeTranslation);
                main_ui.find('.collaborative-translation-main-close a').click(closeCollaborativeTranslation);
            }

            var setMainZones = function() {
                main_ui = $('body').find(".collaborative-translation-ui").eq(0);
                outer_zone = main_ui.find(".collaborative-translation-outer-zone");
                translation_zone = main_ui.find(".collaborative-translation-workplace-translation-language");
                is_html = trigger_link.prev(".collab-translation-is-html").length;
            }

            var initCollaborativeTranslation = function() {
                var href = trigger_link.attr('href');
                $.ajax({
                    url: href,
                    type: "GET",
                    async: true,
                    success: function(response){
                        $('body').append(response);
                        setMainZones();
                        var link = main_ui.find(".collaborative-translation-edit-translation-url").text();
                        setTranslationZone(link);
                        setCollaborativeTranslationActions();
                        main_ui.show(400);
                    }});
                return false;
            }

            var closeCollaborativeTranslation = function() {
                $(".collaborative-translation-ui").hide(400, function() {
                   if (is_html) {
                       textarea_id = translation_zone.find('textarea').attr('id');
                       if (typeof(textarea_id)!='undefined')
                           tinyMCE.execCommand('mceRemoveControl', false, textarea_id);
                   }
                   $(this).remove();
                });
                return false;
            }

            initTrigger();
        });
    }

    $(document).ready(function () {
        $(".collab-translation-trigger a").CollaborativeTranslation();
    });
})(jQuery);
