(function ($) {
    var link = '<a href="#" class="internalLinkUrl"></a>'
    var internallinksurl = '/internal-links/'

    function initURLField() {
        input = $(this);
        input.addClass('withInternalLinkUrl');
        input.after(link);
        input.parent().find('a.internalLinkUrl').click(function() {
            popup=window.open(internallinksurl , "Internal links" , "width=850,height=600,scrollbars=YES");
            window.return_value_in = input;
            return false;
        });
    }

    $(document).ready(function () {
        $("input.vURLField").each(initURLField);
    });

})(jQuery);
