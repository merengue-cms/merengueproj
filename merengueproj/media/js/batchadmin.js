jQuery(function($) {
    // Why only store the checkbox selector below and not the result? Because
    // if another piece of JavaScript fiddles with rows on the page
    // (think AJAX delete), modifying the stored checkboxes later may fail.
    var actionForm = $('#batch-action-form');
    var checkboxSelector = 'tr input.batch-select';
    var selectButtons = actionForm.find('button[name=select_all]');
    var deselectButtons = actionForm.find('button[name=deselect_all]');
    
    var checker = function(checked) {
        return function(e) {
            if (checked) {
                selectButtons.hide();
                deselectButtons.show();
            }
            else {
                deselectButtons.hide();
                selectButtons.show();
            }
            actionForm.find(checkboxSelector).each(function() {
                this.checked = checked;
                $(this).change();
            });
        }
    }
    selectButtons.click(checker(true)).show(); // Unhide select buttons.
    deselectButtons.click(checker(false));
    
    // Highlight selected rows on change, and trigger the change event in
    // case any are selected by default.
    actionForm.find(checkboxSelector).change(function(e) {
        var row = $(this).parents('tr');
        if (this.checked) { row.addClass('selected'); }
        else { row.removeClass('selected'); }
    }).change();
});