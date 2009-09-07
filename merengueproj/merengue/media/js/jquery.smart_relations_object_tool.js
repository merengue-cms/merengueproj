(function($) {
    $.fn.sr_tool = function () {
        return this.each(function () {
            var container = $(this);
            var active = $(this).find('li.selected');
            container.addClass('din_smart_relations_object_tool'); 
            if (active.length) {
                container.after(active);
            } else {
                container.after('<li class="void_link"><a class="launch_smart_trigger" href="">-----</a></li>');
                active=container.next('li.void_link');
            }
            container.hide();
            active.addClass('din_selected');
            active.append('<a href="" class="din_smart_trigger launch_smart_trigger"></a>');
            active.find('a.launch_smart_trigger').click(function() {
                container.toggle();
                $(this).parent('li').find('.din_smart_trigger').toggleClass('din_smart_trigger_open');
                return false;
            });
        });
    };

    $(document).ready(function(){
        $('.smart_relations_object_tool').sr_tool();
    });
})(jQuery);
