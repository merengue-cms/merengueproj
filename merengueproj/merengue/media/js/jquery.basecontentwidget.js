(function($) {
    $.fn.basecontent_widget = function () {
        return this.each(function () {
            var container = $(this);
            var select = container.find('select').eq(0);
            var info = container.find('span.selected_content').eq(0);
            $(window).focus(function() {
                var name = select.find('option:selected').html();
                info.html(name);
            });
            $(window).triggerHandler('focus');
        });
    };

    $(document).ready(function(){
        $('.RelatedBaseContentWidget').basecontent_widget();
    });
})(jQuery);
