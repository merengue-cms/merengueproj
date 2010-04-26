(function ($) {
    $.fn.DocumentSection = function (doc) {
        return this.each(function () {
            var section_document = doc;
            var section = $(this);
            var trigger_menu_link = $(this).find('a.document-section-actions-trigger');
            var section_menu = $(this).find('.document-section-actions');
            var insert_after = $(this).find('.document-section-insert-after-trigger a');
            var delete_trigger = $(this).find('.document-section-delete');
 
            var initTrigger = function() {
                insert_after.click(addDocumentSection);
            }

            var addDocumentSection = function() {
                var href = insert_after.attr('href');
                $.ajax({
                    url: href,
                    type: "GET",
                    async: true,
                    success: function(response){
                        section.after(response);
                        new_section = section.next(".document-section");
                        if (typeof($.fn.CollaborativeComments)!='undefined')
                            new_section.find(".collab-comment-trigger a").CollaborativeComments();
                        if (typeof($.fn.CollaborativeTranslation)!='undefined')
                            new_section.find(".collab-translation-trigger a").CollaborativeTranslation();
                	new_section.DocumentSection(doc);
                        new_section.find(".document-section-insert-after-trigger a").DocumentSection();
                    }});
                return false;
            };

            var hideSectionMenu = function() {
                section_menu.hide();
                section.removeClass('document-section-active');
            };

            var displaySectionMenu = function() {
                section_document.find('.document-section-active').trigger('close-menu');
                section_menu.show();
                section.addClass('document-section-active');
            };

            var toggleSectionMenu = function() {
                if (section.hasClass('document-section-active')) {
                    hideSectionMenu();
                } else {
                    displaySectionMenu();
                }
                return false;
            };

            var deleteSection = function() {
                var trigger = $(this);
                var href = trigger.attr('href');
                $.ajax({
                    url: href,
                    type: "GET",
                    async: true,
                    dataType: 'json',
                    success: function(response){
                        if (!response.errors) {
                            section.hide('slow');
                        }
                    }});
                return false;
            };

            var initSectionMenu = function() {
                trigger_menu_link.click(toggleSectionMenu);
            };

            var bindListeners = function() {
                section.bind('close-menu', hideSectionMenu);
                delete_trigger.bind('click', deleteSection);
            };

            var initSection = function() {
                initTrigger();
                initSectionMenu();
                bindListeners();
            };

            initSection();
        });
    }

    $.fn.MerengueDocument = function () {
        return this.each(function () {
            var doc = $(this);

            var initDocument = function() {
                doc.find('.document-section').DocumentSection(doc);
            };

            initDocument();
        });
    }

    $(document).ready(function () {
        $(".merengue-document").MerengueDocument();
    });
})(jQuery);
