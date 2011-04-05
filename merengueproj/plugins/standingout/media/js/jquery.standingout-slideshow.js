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

        var mediaurl = $(".standingout-slideshow .standing-out-media-url").text();
        Shadowbox.init({
                assetUrl: mediaurl,
                loadingImage: mediaurl + 'merengue/img/multimedia/loading.gif',
                displayNav: true,
                displayClose: true,
                continuous: true,
                enableKeys: false
        });

        Shadowbox.setup($('div.standingout-video a'), {
                autoplayMovies: true,
                flvPlayer: mediaurl + 'merengue/flash/flvplayer.swf'
        });
    });
})(jQuery);
