(function($) {
    $.fn.mainTabs = function () {
        return this.each(function () {
            var container = $(this);
            var tabs = container.find('li');

            var activateTab = function() {
                var tab = $(this).parent('li');
                var link = $(this).attr('href').split('#')[1];
                tabs.removeClass('active');
                tab.addClass('active');
                $('.module-merengue').hide();
                $('#' + link).show();
                return false;
            };

            var initTriggers = function() {
                tabs.find('a').click(activateTab);
            };

            var initTabs = function() {
                $('.module-merengue').hide();
            };

            var firstTab = function() {
                var link = 'contentmanagement';
                if (location.href.indexOf('#') > -1) {
                    link = location.href.split('#')[1];
                };
                container.find('.' + link + ' a').triggerHandler('click');
            };

            initTabs();
            initTriggers();
            firstTab();
        });
    };

    $(document).ready(function(){
        $('.maintabs').mainTabs();
    });
})(jQuery);
