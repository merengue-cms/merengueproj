(function ($) {
    $.fn.CollaborativeComments = function () {
        return this.each(function () {
            var trigger_link = $(this);
            var main_ui = null;
            var outer_zone = null;
            var main_zone = null;
            var recount_url = null;
            var recount_container = null;
            var minimal_height = 300;
            var initial_height = null;
 
            var initTrigger = function() {
                trigger_link.click(initCollaborativeComments);
            }

            var recountComments = function() {
                $.ajax({
                    url: recount_url,
                    type: "GET",
                    async: true,
                    dataType: "json",
                    success: function(response){
                        $('body').find(recount_container).html(response.num || "0");
                    }});
            }

            var boundRevisorForm = function(action_div) {
                var comment_main_div = action_div.parents('.collaborative-comments-item');
                action_div.find('#collab-comments-revise-comment-form').ajaxForm({
                    success: function(response, status) {
                        var href = comment_main_div.find('.collaborative-comments-item-update-url').text();
                        $.ajax({
                            url: href,
                            type: "GET",
                            async: true,
                            success: function(commenthtml){
                                comment_main_div.after(commenthtml);
                                var new_comment_div = comment_main_div.next('.collaborative-comments-item');
                                comment_main_div.remove();
                                var action_div = new_comment_div.find('.collaborative-comments-item-revisor-actions');
                                action_div.html(response);
                                boundRevisorForm(action_div);
                                setCommentActions(new_comment_div);
                            }
                        });
                    }
                });
            }

            var initRevisorForm = function(revisor_div) {
                var trigger = revisor_div.find('.collaborative-comments-item-revisor-trigger');
                var comment_main_div = revisor_div.parents('.collaborative-comments-item');


                $.ajax({
                    url: trigger.attr('href'),
                    type: "GET",
                    async: true,
                    success: function(response){
                        var action_div = comment_main_div.find('.collaborative-comments-item-revisor-actions');
                        action_div.html(response);
                        boundRevisorForm(action_div);
                    }});
                return false;
            }

            var setCommentActions = function(container) {
                container.find('a.collaborative-comments-item-revisor-trigger').click(function() {
                    var revisor_div = $(this).parent('.collaborative-comments-item-revisor');
                    initRevisorForm(revisor_div);
                    return false;
                });

                container.find('.collaborative-comments-item-status-history a.toggle').click(function() {
                    $(this).parent().find('.collaborative-comments-item-status').toggle(400);
                    return false;
                });

                container.find('.collaborative-comments-item-status-history').each(function() {
                    if (!$(this).find('.collaborative-comments-item-status').length) {
                        $(this).hide();
                    }
                });
            }

            var setFolderActions = function(folder) {
                folder.find('#collab-comments-add-comment-form').ajaxForm({
                    success: function(response, status) {
                        folder.html(response);
                        recountComments();
                        setFolderActions(folder);
                    }
                });
 
                setCommentActions(folder);
            }

            var selectActiveFolder = function() {
                var trigger = $(this);
                var href = trigger.attr('href');
                var folder_id = trigger.attr('target');
                trigger.parents('ul').eq(0).find('li.selected').removeClass('selected');
                trigger.parent('li').addClass('selected');
                main_ui.find('.collaborative-comments-folder').hide();
                var folder = main_ui.find(folder_id);
                $.ajax({
                    url: href,
                    type: "GET",
                    async: true,
                    success: function(response){
                        folder.html(response).show();
                        setFolderActions(folder);
                        fheight = folder.height() + folder.parent().position().top + 30;
                        main_zone.css('height', initial_height);
                        minitial = main_zone.height();
                        if (fheight > minimal_height && fheight < minitial ) {
                            main_zone.height(fheight);
                        }
                    }});
                return false;
            }

            var loadMainFolder = function() {
                main_ui.find('#collaborative-comments-main-folder-trigger').click();
            }

            var setCollaborativeCommentsActions = function() {
                outer_zone.click(closeCollaborativeComments);
                main_ui.find('.collaborative-comments-main-close a').click(closeCollaborativeComments);
                main_ui.find('.collaborative-comments-folder-selector a').click(selectActiveFolder);
            }

            var setMainZones = function() {
                main_ui = $('body').find(".collaborative-comments-ui").eq(0);
                main_zone = main_ui.find('.collaborative-comments-main');
                initial_height = main_zone.css('height');
                outer_zone = main_ui.find(".collaborative-comments-outer-zone");
                recount_url = main_ui.find(".collaborative-comments-hidden-parameters #collaborative-comment-update-num-url").text();
                recount_container = main_ui.find(".collaborative-comments-hidden-parameters #collaborative-comment-num-comments-container").text();
            }

            var initCollaborativeComments = function() {
                var href = trigger_link.attr('href');
                $.ajax({
                    url: href,
                    type: "GET",
                    async: true,
                    success: function(response){
                        $('body').append(response);
                        setMainZones();
                        setCollaborativeCommentsActions();
                        loadMainFolder();
                        recountComments();
                        main_ui.show(400);
                    }});
                return false;
            }

            function closeCollaborativeComments() {
                $(".collaborative-comments-ui").hide(400, function() {
                   $(this).remove();
                });
                return false;
            }

            initTrigger();
        });
    }

    $(document).ready(function () {
        $(".collab-comment-trigger a").CollaborativeComments();
    });
})(jQuery);
