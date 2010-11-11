var Collection = null;

(function ($) {
    $.fn.CollectionForm = function () {
        return this.each(function () {
            var form = $(this);
 
            var initTriggers = function() {
                form.bind('redisplay', parseContentTypes);
            }

            var parseContentTypes = function() {
                var content_types = form.find('#id_content_types_to');
                cts = '';
                content_types.find('option').each(function() {
                   cts += $(this).val();
                   cts += ',';
                });               
                cts = cts.slice(0,-1);
                if (!cts) {
                	return;
		}
		doAjax(cts);
            }

            var populate = function(select, fields) {
                var actual = select.find('option:selected').val();
                box = select.get(0);
                box.options.length = 0; // clear all options
                for (var i = 0, j = fields.length; i < j; i++) {
                    selected = (fields[i] == actual);
                    selected_default = (fields[i] == '');
                    box.options[box.options.length] = new Option(fields[i], fields[i], selected_default, selected);
                }
            }

            var doAjax = function(cts) {
                href = '/cms/collection/ajax/get_collection_fields/';
                $.ajax({
                    url: href,
                    type: "GET",
                    data: {content_types: cts},
                    dataType: 'json',
                    async: true,
                    success: function(response){
                        $('td.filter_field select').each(function() {
                            populate($(this), response.fields);
                        });
                        $('td.field_name select').each(function() {
                            populate($(this), response.fields_no_lang);
                        });
                        populate($('#id_group_by'), response.fields_no_lang);
                        populate($('#id_order_by'), response.fields_no_lang);
                    }
                });
                return false;
            }

            initTriggers();
        });
    }

    $(document).ready(function () {
        Collection = $("#collection_form").CollectionForm();
    });
})(jQuery);

