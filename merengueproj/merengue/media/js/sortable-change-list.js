// Based http://www.djangosnippets.org/snippets/1053/
jQuery(function($) {
    var draggable_base = $(".draggable-icon");

    //$(".module table").css('table-layout', 'fixed');
    $(".module table tbody tr").each(function(index, row) {
        $(row).find('th').eq(0).prepend(draggable_base.clone().show());
        $(row).find('input.action-select').parent('td').css('width', '1%');
    });

    if ($("#save-order-form").length == 0){
        return
    }
    $('.module table tbody').sortable({
        items: 'tr',
        containment: 'document',
        tolerance: 'pointer',
        placeholder: 'row-holder',
        axis: 'y',
        forceHelperSize: true,
        forcePlaceholderSize: true,
        handle: '.draggable-icon',
        update: function() {
            var neworder = [];
            $(this).find('tr').not('.ui-sortable-helper').find('input').each(function(i, o) {
                neworder[neworder.length] = o.value;
                var row = $(this).parents('tr');
                row.removeClass('row1').removeClass('row2');
                row.addClass('row' + (i%2+1));
                row.find('.draggable-icon').css('background-position', 'bottom center');
            });
            $('input[name=neworder]').attr('value',neworder);
            $("#save-order-form").show()
        },
        change: function(event, ui) { 
            ui.placeholder.css('width', ui.helper.css('width'));
            ui.placeholder.css('height', ui.helper.css('height'));
            $(this).find('tr').not(ui.item).each(function(i, o) {
                var row;
                if ($(o).hasClass('row-holder')) {
                    row = ui.helper;
                } else {
                    row = $(o);
                }
                row.removeClass('row1').removeClass('row2');
                row.addClass('row' + (i%2+1));
            });
            if (ui.item.hasClass('row1')) {
                ui.helper.addClass('row1');
            } else {
                ui.helper.addClass('row2');
            }
        },
        start: function(event, ui) { 
            var tds = ui.item.children();
            $(this).find('.draggable-icon').css('background-position', 'top center');
            ui.helper.find('.draggable-icon').css('background-position', 'bottom center');
            ui.helper.children().each(function(i, o) {
                $(this).css('width', tds.eq(i).css('width'));
            });
        }
    });
});
