// use $(document).loadcomments(); to reload comments functionality on ajax load

(function($) {
        var error_message = $('#comment-error').html();
        if ($.browser.msie){
            $.ajaxSetup({cache:false});
        }
        var postJSON = function(options){
            $.ajax({
               type: "POST",
               dataType: 'json',
               url: options.url,
               data: options.data ? 'undefined': 'none',
               error: options.error ? 'undefined': function(XMLHttpRequest, textStatus, errorThrown) {
                    alert(error_message);
               },
               success: options.success
            });
        }

        var sendcomment = function (){
            var comment_url = $(this).attr('action');
            var data = $(this).find("input,textarea");
            var form = $(this);
            data = $.param(data);
            $.ajax({
               type: "POST",
               url: comment_url,
               data: data,
               error: function( XMLHttpRequest, textStatus, errorThrown) {
                   form.find('.submit').attr('disabled',0);
                   show_error_message(form, error_message);
               },
               success: function(datapost){
                    var comment_body = form.parent().parent();
                    comment_body.children('.commentresults').hide();
                    comment_body.children('.commentresults').html(datapost);
                    if (comment_body.children('.commentresults').find('form').length){
                        comment_body.children('.commentresults').find('form').hide();
                        comment_body.children('.commentform').find('form').replaceWith(comment_body.children('.commentresults').find('form'));
                        comment_body.children('.commentresults').empty();
                        comment_body.children('.commentform').find('form').submit(sendcomment);
                        if (comment_body.find("[id=id_name]").val()){
                            comment_body.find("[id=id_name]").parent().hide()
                        }
                        comment_body.children('.commentform').find('form').show('slow');
                        form.find('.submit').attr('disabled',0);
                    }
                    else {
                        comment_body.children('.commentresults').children('div').hide();
                        if (comment_body.children('div.comment').length){
                            comment_body.children('div.comment:last').after(comment_body.children('.commentresults').children('div'));
                        }
                        else {
                            comment_body.children('div.commentform').before(comment_body.children('.commentresults').children('div'));
                        }
                        comment_body.children('.commentresults').empty();
                        comment_body.children('.commentform').empty();
                        comment_body.children('div.comment:last').find('a.addReply').show();
                        comment_body.children('div.comment:last').show('slow');
                        comment_body.find('.comment a.hideReply').unbind('click').click(hide_reply);
                        comment_body.find('.comment a.addReply').unbind('click').click(add_reply);
                        comment_body.find('.comment a.publishComment').unbind('click').click(change_visibility);
                        comment_body.find('.comment a.censureComment').unbind('click').click(change_visibility);
                        comment_body.find('.comment a.deleteComment').unbind('click').click(delete_comment);
                        comment_body.trigger('added-new-comment');
                    }
                    comment_body.children('.actions').find('.hideReply').hide();
                    comment_body.children('.actions').find('.addReply').show();
                    form.hide('slow');
                    var captcha_src = $('.commentform #captcha-image').attr('src');
                    $('.commentform #captcha-image').attr('src', '');
                    var now = new Date();
                    $('.commentform #captcha-image').attr('src', captcha_src + '?_=' +now.getTime());
                }
            });
            form.find('.submit').attr('disabled',1);
            return false;
        }

        var add_reply = function(){
            var action = $(this);
            var actions = $(this).parent();
            var container = $(this).parent().parent();
            var comment_url = action.attr('href');
            var reply_action = $(this);
            container.children("div.commentform").hide();
            if (!container.children('div.commentform').html()){
                container.children('div.commentform').load(comment_url, function(data, textStatus){
                    if (textStatus!='success'){
                        // put a error message here
                        show_error_message(container, error_message);
                        return false;
                    }
                    reply_action.hide();
                    actions.children('.hideReply').show();
                    $(this).children("form").submit(sendcomment);
                    if ($(this).children("form").find("#id_name").val()){
                        $(this).children("form").find("#id_name").parent().hide();
                    }
                    $(this).show('slow');
                });
            }
            else {
                container.children('div.commentform').show('slow');
            }
            return false;
        };

        var hide_reply = function () {
            var action = $(this);
            var actions = $(this).parent();
            var container = $(this).parent().parent();
            var comment_url = action.attr('href');
            var msg = container.find('.comment-discard-message:first').text();
            if (msg && !confirm(msg)) {
                return false;
            }
            $(this).hide();
            actions.children('.addReply').show();
            container.children('div.commentform').hide('slow', function(){$(this).empty()});
            return false;
        };

        var change_visibility = function () {
            var change_visibility_url = $(this).attr('href');
            var actions = $(this).parent();
            var container = $(this).parent().parent();
            postJSON({url:change_visibility_url,
                      error: function (datapost){
                            // put a error message here
                            show_error_message(container, error_message);
                            },
                      success: function (datapost){
                         if (datapost.is_public){
                            actions.addClass('public');
                            container.children('h3, .commentinfo, .commentBody, .actions').removeClass('censured');
                         }
                         else {
                            actions.removeClass('public');
                            container.children('h3, .commentinfo, .commentBody, .actions').addClass('censured');
                         }
                      }
            });
            return false;
        }

        var delete_comment = function () {
            var delete_url = $(this).attr('href');
            var actions = $(this).parent();
            var container = $(this).parent().parent();
            var msg = container.find('.comment-delete-message:first').text();
            if (msg && !confirm(msg)) {
                return false;
            }
            postJSON({
               url: delete_url,
               error: function( XMLHttpRequest, textStatus, errorThrown) {
                    show_error_message(container, error_message);
               },
               success: function(datapost){
                           container.hide('slow', function(){ $(this).remove() });
               }
            });
            return false;
        }

        var show_error_message = function (container, msg){
            if (!container.children('.errormessage').length){
                container.prepend('<div class="errormessage" style="opacity:0">' + msg + '</div>');
            }
            else {
                container.children('.errormessage').html(msg);
            }
            container.children('.errormessage').animate({opacity:1}, 500).animate({opacity:1}, 5000).animate({opacity:0}, 500, function(){
                $(this).remove();
            });
        }

        $.fn.loadcomments = function (options) {
           var opts = $.extend({}, {}, options);
            $('.comment').each(function() {
                $(this).find('a.publishComment:first').click(change_visibility);
                $(this).find('a.censureComment:first').click(change_visibility);
                $(this).find('a.deleteComment:first').click(delete_comment);
                $(this).find('a.hideReply:first').click(hide_reply);
                $(this).find('a.addReply:first').click(add_reply);
            });
            $('div#firstcomment').each(function() {
                $(this).find('a.hideReply:first').click(hide_reply);
                $(this).find('a.addReply:first').click(add_reply);
           });
           return this;
       }
})(jQuery);
