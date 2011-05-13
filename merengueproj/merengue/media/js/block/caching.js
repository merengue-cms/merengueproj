(function($) {
    function toggle_cache_params(flag) {
        // enable/disable the caching parameters
        $("#id_cache_only_anonymous").attr('disabled', !flag);
        $("#id_cache_vary_on_url").attr('disabled', !flag);
        $("#id_cache_vary_on_language").attr('disabled', !flag);
        $("#id_cache_vary_on_user").attr('disabled', !flag);
    }

    $(document).ready(function() {
        // disable the caching params if cache is not enabled
        if (!$("#id_is_cached").attr("checked")) {
            toggle_cache_params(false);
        }
        // enable/disable the caching params depends on cache
        $("#id_is_cached").click(function () {
            if ($("#id_is_cached").attr("checked")) {
                toggle_cache_params(true);
            }
            else {
                toggle_cache_params(false);
            }
        });
    });
})(jQuery);
