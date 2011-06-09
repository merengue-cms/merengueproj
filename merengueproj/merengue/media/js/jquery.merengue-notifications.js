(function($) {
    $.fn.MessageBox = function () {
        return this.each(function () {
            var box = $(this);
            var notifications = $('#notifications');
            var messages = box.find('#info-list li');
            
            notifications.notify();
            messages.each(function() {
                var message = $(this);

                notifications.notify("create", "basic-template", {
                    text: message.text(),
                    classes: message.find('span').attr('class')
                });
            });
        });
    };

    $(document).ready(function(){
        $('#messagebox').MessageBox();
    });
})(jQuery);
