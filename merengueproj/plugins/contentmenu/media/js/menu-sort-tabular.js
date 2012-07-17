// Based http://www.djangosnippets.org/snippets/1053/
jQuery(function($) {
    var update_order = function() {
        $(this).find('tr').each(function(i) {
            if ($(this).find('.basecontent input[type=hidden]').val()) {
                $(this).find('input[id$=order]').val(i);
                var icons = $(this).find('.iconic');
                if (icons.length > 1) {
                    icons.not(icons.eq(0)).remove();
                }
            }
            if (i % 2 == 0){
                $(this).removeClass('row2');
                $(this).addClass('row1');
            }
            else {
                $(this).removeClass('row1');
                $(this).addClass('row2');
            }
        });
    }
    var reattach = function() {
        $('.module table tbody').sortable({
            items: 'tr',
            handle: 'td',
            update: update_order
        });
    }
    reattach();
    $('div.tabular').each(update_order);
    $('div.tabular td').css('cursor', 'move');
    $('div.tabular table').find('input[id$=order]').parent('td').hide();
    $('div.tabular table thead th:last').prev().hide();
    $('div.tabular table').find('div').live('added', function() {
        $('div.tabular').each(update_order);
    });
});
