(function ($) {
    $(document).ready( function () {
        $(".slidetabs").tabs(".standingout-slidecontainer > div.standingout-slide", {
            effect: 'fade',
            fadeOutSpeed: "slow",
            rotate: true
        }).slideshow({
            clickable: false
        });

        $(".standingout-slideshow a.backward").click(function() {
            return false;
        });

        $(".standingout-slideshow a.forward").click(function() {
            return false;
        });
    });
})(jQuery);
