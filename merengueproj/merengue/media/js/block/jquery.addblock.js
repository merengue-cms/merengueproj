(function($){
    var addingblocks = false;
    $("a#activate-add-block").click(function () {
        if (addingblocks) {
            $(".add-block-in-container").hide();
            addingblocks = false;
        } else {
            $(".add-block-in-container").show();
            addingblocks = true;
        }
        return false;
    });
})(jQuery);
