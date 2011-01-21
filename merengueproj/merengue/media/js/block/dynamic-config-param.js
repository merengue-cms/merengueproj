(function ($) {
    var config_content = '';
    var update_block_config = function() {
        var selected_block = $("#id_block").val()
        if (selected_block != "") {
            $.ajax({
                url: '/cms/blocks/config/ajax/' + selected_block,
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
    }

    $(document).ready(function () {
        config_content = $(".form-row.config").html();
        update_block_config();
        $(".block #id_block").change(function(){
            update_block_config();
        });
    });
}(jQuery));