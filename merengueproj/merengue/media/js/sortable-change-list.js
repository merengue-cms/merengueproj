// Based http://www.djangosnippets.org/snippets/1053/
jQuery(function($) {
    if ($("#save-order-form").length == 0){
        return
    }
    $('.module table tbody').sortable({
        items: 'tr',
        containment: 'parent',
        tolerance: 'pointer',
        delay: 500,
        placeholder: 'row-holder',
        axis: 'y',
        forceHelperSize: true,
        forcePlaceholderSize: true,
        update: function() {
            var neworder = [];
            $(this).find('tr').not('.ui-sortable-helper').find('input').each(function(i, o) {
                neworder[neworder.length] = o.value;
                $(this).parents('tr').removeClass('row1').removeClass('row2');
                $(this).parents('tr').addClass('row' + (i%2+1));
            });
            $('input[name=neworder]').attr('value',neworder);
            $("#save-order-form").show()
        },
        change: function(event, ui) { 
            ui.placeholder.css('width', ui.helper.css('width'));
            $(this).find('tr').not('.ui-sortable-helper').find('input').each(function(i, o) {
                $(this).parents('tr').removeClass('row1').removeClass('row2');
                $(this).parents('tr').addClass('row' + (i%2+1));
            });
            ui.helper.removeClass('row1').removeClass('row2');
            if (ui.item.hasClass('row1')) {
                ui.helper.addClass('row1');
            } else {
                ui.helper.addClass('row2');
            }
        },
        start: function(event, ui) { 
            var tds = ui.item.children();
            ui.helper.children().each(function(i, o) {
                $(this).css('width', tds.eq(i).css('width'));
            });
        }
    });
});
