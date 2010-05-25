(function($) {
    $.fn.sr_tool = function () {
        return this.each(function () {
            var container = $(this);
            var size = container.find('li').length
            var active = $(this).find('li.parent');

            var toggleMenu = function() {
                container.toggle();
                $('.din_smart_relations_object_tool').not(container).hide();
                var trigger = $(this).parent('li').find('.din_smart_trigger');
                $('.din_smart_trigger').not(trigger).removeClass('din_smart_trigger_open');
                trigger.toggleClass('din_smart_trigger_open');
                return false;
            };

            container.addClass('din_smart_relations_object_tool'); 
            if (active.length) {
                container.after(active);
            } else {
                container.after('<li class="parent"><a class="launch_smart_trigger" href="">-----</a></li>');
                active=container.next('li.parent');
            }
            container.hide();
            if (size>1) {
                active.addClass('din_selected');
                active.append('<a href="" class="din_smart_trigger launch_smart_trigger"></a>');
                active.find('a').click(toggleMenu);
            }
        });
    };

    $(document).ready(function(){
        $('.smart_relations_object_tool').sr_tool();
    });
})(jQuery);
