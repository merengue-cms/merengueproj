(function ($) {
    var tinymce_settings = {
        script_url : '../../../cmsutils/js/widgets/tiny_mce/tiny_mce.js',
        mode: 'none',
        width: "100%",
        height: "100%",
        plugins: "preview,paste,fullscreen",
        button_tile_map: true,
        apply_source_formatting: false,
        theme_advanced_toolbar_align: "left",
        theme_advanced_blockformats: "h1,h2,h3",
        theme_advanced_disable: "",
        theme_advanced_resizing: false,
        theme_advanced_resize_horizontal: false,
        theme_advanced_toolbar_location: "top",
        theme_advanced_buttons1: "bold,italic,underline,justifyleft,justifycenter,justifyright,bullist,numlist,outdent,indent",
        theme_advanced_buttons2: "formatselect,link,image,code,fullscreen",
        theme_advanced_buttons3: "",
        theme_advanced_buttons4: "",
        theme: "advanced",
        editor_deselector: "mceNoEditor",
        extended_valid_elements: "hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]"
    };

    $.fn.DocumentSection = function (doc, options) {
        return this.each(function () {
            var section_document = doc;
            var section = $(this);
            var section_id = null;
            var trigger_menu_link = $(this).find('a.document-section-actions-trigger');
            var section_menu = $(this).find('.document-section-actions');
            var edit_buttons = section_document.find('.merengue-document-helpers .document-section-edition');

            /* Menu display/hide */
            var initSectionMenu = function() {
                trigger_menu_link.click(toggleSectionMenu);
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

            /* Section functionallity: insert, edit, delete */
            var insertSection = function() {
                var url = options['section_insert_url'];
                $.ajax({
                    url: url,
                    type: 'GET',
                    cache: false,
                    async: true,
                    dataType: 'html',
                    data: {document_section_id: section_id,
                           document_id: options['document_id']},
                    success: function(response){
                        section.after(response);
                        new_section = section.next(".document-section");
                        new_section.hide();
                        if (typeof($.fn.CollaborativeComments)!='undefined')
                            new_section.find(".collab-comment-trigger a").CollaborativeComments();
                        if (typeof($.fn.CollaborativeTranslation)!='undefined')
                            new_section.find(".collab-translation-trigger a").CollaborativeTranslation();
                	new_section.DocumentSection(doc, options);
                        hideSectionMenu();
                        new_section.show('slow');
                    }
                });
                return false;
            };

            var deleteSection = function() {
                var url = options['section_delete_url'];
                $.ajax({
                    url: url,
                    cache: false,
                    type: "GET",
                    async: true,
                    dataType: 'json',
                    data: {document_section_id: section_id,
                           document_id: options['document_id']},
                    success: function(response){
                        if (!response.errors) {
                            section.hide('slow');
                        }
                    }});
                return false;
            };

            var editSection = function() {
                var body = section.find('.document-section-body');
                var newbody = section.find('.new-document-section-body');
	        hideSectionMenu();
                if (newbody.length) {
                    return false;
                }
                newbody = body.clone();
                body.after(newbody);
                body.hide();
                newbody.addClass('new-document-section-body');
                newbody.after(edit_buttons.clone());
                newbody.tinymce(tinymce_settings);
                bindEditButtons();
                return false;
            };

            var cancelEdition = function() {
                var body = section.find('.document-section-body');
                var newbody = section.find('.new-document-section-body');
                newbody.tinymce().hide();
                newbody.remove();
                section.find('.document-section-edition').remove();
                body.show();
                return false;
            };

            var performEdition = function() {
                var body = section.find('.document-section-body');
                var newbody = section.find('.new-document-section-body');
                var url = options['section_edit_url'];
                $.ajax({
                    url: url,
                    cache: false,
                    type: "POST",
                    async: true,
                    dataType: 'json',
                    data: {document_section_id: section_id,
                           document_id: options['document_id'],
                           document_section_body: newbody.tinymce().getContent()},
                    success: function(response){
                        if (!response.errors) {
                            newbody.tinymce().hide();
                            newbody.remove();
                            section.find('.document-section-edition').remove();
                            body.html(response.body);
                            body.show();
                        }
                    }});
                return false;
            };

            var bindEditButtons = function() {
                section.find('.cancel-edition').bind('click', cancelEdition);
                section.find('.save-edition').bind('click', performEdition);
            };

            var bindListeners = function() {
                var edit_trigger = section_menu.find('.document-section-edit');
                var insert_trigger = section_menu.find('.document-section-insert');
                var delete_trigger = section_menu.find('.document-section-delete');

                edit_trigger.bind('click', editSection);
                insert_trigger.bind('click', insertSection);
                delete_trigger.bind('click', deleteSection);
                section.bind('close-menu', hideSectionMenu);
            };

            var initConfig = function() {
                section_id = section.find('.document-section-config .document-section-id').text();
            };

            var initSection = function() {
                initConfig();
                initSectionMenu();
                bindListeners();
            };

            initSection();
        });
    }

    $.fn.MerengueDocument = function () {
        return this.each(function () {
            var doc = $(this);
            var config_div = doc.find('.merengue-document-conf');
            var settings = {};

            var getSettings = function() {
                var section_insert_url = config_div.find('.section-insert-url').text();
                var section_delete_url = config_div.find('.section-delete-url').text();
                var section_edit_url = config_div.find('.section-edit-url').text();
                var section_delete_message = config_div.find('.section-delete-message').text();
                var document_id = config_div.find('.document_id').text();

                return {
                    section_insert_url: section_insert_url,
                    section_delete_url: section_delete_url,
                    section_edit_url: section_edit_url,
                    section_delete_message: section_delete_message,
                    document_id: document_id
                }
            };

            var insertFirstSection = function() {
                var url = settings['section_insert_url'];
                trigger = $(this);
                $.ajax({
                    url: url,
                    type: 'GET',
                    cache: false,
                    async: true,
                    dataType: 'html',
                    data: {document_id: settings['document_id']},
                    success: function(response){
                        trigger.after(response);
                        new_section = trigger.next(".document-section");
                        new_section.hide();
                        if (typeof($.fn.CollaborativeComments)!='undefined')
                            new_section.find(".collab-comment-trigger a").CollaborativeComments();
                        if (typeof($.fn.CollaborativeTranslation)!='undefined')
                            new_section.find(".collab-translation-trigger a").CollaborativeTranslation();
                	new_section.DocumentSection(doc, settings);
                        new_section.show('slow');
                    }
                });
                return false;
            };

            var initDocument = function() {
                settings = getSettings();
                doc.find('.insert-first-section').click(insertFirstSection);
                doc.find('.document-section').DocumentSection(doc, settings);
            };

            initDocument();
        });
    }

    $(document).ready(function () {
        $(".merengue-document").MerengueDocument();
    });
})(jQuery);
