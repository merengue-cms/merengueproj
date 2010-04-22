(function($) {
    $.fn.basecontent_widget = function () {
        return this.each(function () {
            var container = $(this);
            var select = container.find('select').eq(0);
            var info = container.find('span.selected_content').eq(0);
            var remove = container.find('span.remove_current').eq(0);
 
            remove.find('img').click(function() {
                var cancel = select.find('option[value=""]');
                var name = cancel.html();
                cancel.attr('selected', 'selected');
                info.html(name);
            });

            $(window).focus(function() {
                var selected = select.find('option:selected');
                var name = selected.html();
                info.html(name);
                if (selected.val() != '') {
                    remove.show();
                }
            });
            $(window).triggerHandler('focus');
        });
    };

    $(document).ready(function(){
        $('.RelatedBaseContentWidget').basecontent_widget();
    });
})(jQuery);
