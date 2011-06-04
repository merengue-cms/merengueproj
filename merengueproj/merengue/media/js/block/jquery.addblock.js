(function($){
    var addingblocks = false;
    $("a#activate-add-block").click(function () {
        if (addingblocks) {
            $(".add-block-in-container").hide();
            $(".blockContainerPlace").hide();
            $(".blockContainer").attr("style", "border: none;");
            addingblocks = false;
        } else {
            $(".add-block-in-container").show();
            $(".blockContainerPlace").show();
            $(".blockContainer").attr("style", "border: 1px solid #053EFF;");
            addingblocks = true;
        }
        return false;
    });
})(jQuery);
