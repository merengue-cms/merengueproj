(function($) {
    $.fn.sr_tool = function () {
        return this.each(function () {
            var container = $(this);
            var edit_link = container.find('li.edit-link');
            var content_link = container.find('li.content-link');
            var content_ul = content_link.find('ul');
            var extra_link = container.find('li.extra-link');
            var extra_ul = extra_link.find('ul');
            var more_trigger = extra_link.find('a.trigger');
            var more_trigger_text = more_trigger.text();

            var checkActive = function() {
                container.find('li.selected').addClass('active');
                if (!container.find('li.active').length) {
                    edit_link.addClass('active');
                }
                if (content_ul.find('li.active').length) {
                    content_link.addClass('active');
                }
                if (extra_ul.find('li.active').length) {
                    extra_link.addClass('active');
                }
            };

            var initContentMenu = function() {
                content_ul.append(container.find('li.content_manager'));
                if (content_ul.find('li').length) {
                    content_link.show();
                    var selected = content_ul.find('li.selected');
                    if (selected.length) {
                        var trigger = content_link.find('a.trigger');
                        trigger.text(trigger.text() + ': ' + selected.find('a').text());
                    };
                };
            };

            var initExtraMenu = function() {
                var text = '';
                container.find('> li').each(function() {
                    var newtext = more_trigger_text + ': ' + $(this).find('> a').text();
                    if (newtext.length > text.length) {
                        text = newtext;
                    }
                });
                more_trigger.text(text);
            };

            var initItems = function() {
                container.find('li').hide();
                extra_link.show();
                initContentMenu();
                initExtraMenu();
                var current_height = container.height();
                container.find('li').each(function() {
                    var tab = $(this);
                    if (!tab.hasClass('content-link')) {
                        tab.show();
                    }
                    if (tab.hasClass('content_manager')) {
                        return true;
                    }
                    if (current_height && container.height() > current_height + 10) {
                        extra_ul.append(tab);
                    }
                    if (!current_height) {
                        current_height = container.height();
                    }
                });
                more_trigger.text(more_trigger_text);
                if (extra_ul.find('li').length) {
                    var selected = extra_ul.find('li.selected');
                    if (selected.length) {
                        var trigger = extra_link.find('a.trigger');
                        trigger.text(trigger.text() + ': ' + selected.find('a').text());
                    };
                } else {
                    extra_link.hide();
                };
                checkActive();
            };

            var initTriggers = function() {
                content_link.find('a.trigger').click(function() { content_ul.toggle(); return false; });
                extra_link.find('a.trigger').click(function() { extra_ul.toggle(); return false; });
            };
            initItems();
            initTriggers();
        });
    };

    $(document).ready(function(){
        $('#change-tabs-ul').sr_tool();
    });
})(jQuery);
