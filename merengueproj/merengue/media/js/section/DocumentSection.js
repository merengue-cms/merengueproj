(function ($) {
    $.fn.DocumentSection = function () {
        return this.each(function () {
            var trigger_link = $(this);
 
            var initTrigger = function() {
                trigger_link.click(initDocumentSection);
            }

            var initDocumentSection = function() {
                var href = trigger_link.attr('href');
                $.ajax({
                    url: href,
                    type: "GET",
                    async: true,
                    success: function(response){
                        trigger_link.parent(".document-section-insert-after-trigger").after(response);
                        new_section = trigger_link.parent(".document-section-insert-after-trigger").next(".document-section");
                        if (typeof($.fn.CollaborativeComments)!='undefined')
                            new_section.find(".collab-comment-trigger a").CollaborativeComments();
                        if (typeof($.fn.CollaborativeTranslation)!='undefined')
                            new_section.find(".collab-translation-trigger a").CollaborativeTranslation();
                        new_section.find(".document-section-insert-after-trigger a").DocumentSection();
                    }});
                return false;
            }

            initTrigger();
        });
    }

    $(document).ready(function () {
        $(".document-section-insert-after-trigger a").DocumentSection();
    });
})(jQuery);
