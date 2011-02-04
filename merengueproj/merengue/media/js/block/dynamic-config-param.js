var update_block_config;

(function ($) {
    var config_content = '';
    update_block_config = function(blocks_index_url) {
        var selected_block = $("#id_block").val()
        if (selected_block != "") {
            $.ajax({
                url: blocks_index_url + 'ajax/config_for_content/' + selected_block,
                success: function(data) {
                    if (data != "") {
                        $(".form-row.config").html(data);
                    } else {
                        $(".form-row.config").html(config_content);
                    }
                }
            });
        } else {
            $(".form-row.config").html(config_content);
        }
    };

    $(document).ready(function () {
        config_content = $(".form-row.config").html();
    });
}(jQuery));