var Collection = null;

(function ($) {
    $.fn.CollectionForm = function () {
        return this.each( function () {
            var form = $(this);

            var initTriggers = function() {
                form.bind('redisplay', parseContentTypes);
                form.find('.filter_operator select').bind('change', replace_filter_value_widget_handler);
                form.find('.filter_operator select').each(function(index, el){
                  replace_filter_value_widget($(el));
                });
                
            }
            var parseContentTypes = function() {
                var content_types = form.find('#id_content_types_to');
                cts = '';
                content_types.find('option').each( function() {
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
                href = $('.collection-get-fields-by-ajax').text();
                $.ajax({
                    url: href,
                    type: "GET",
                    data: {content_types: cts},
                    dataType: 'json',
                    async: true,
                    success: function(response) {
                        $('td.filter_field select').each( function() {
                            populate($(this), response.fields);
                        });
                        $('td.field_name select').each( function() {
                            populate($(this), response.fields_no_lang);
                        });
                        populate($('#id_group_by'), response.fields_no_lang);
                        populate($('#id_order_by'), response.fields_no_lang);
                    }
                });
                return false;
            }
            
            var replace_filter_value_widget_handler = function(event) {
              var element = $(this);
              replace_filter_value_widget(element);
            }
            
            var replace_filter_value_widget = function(element) {                
                var original_input = element.parents('tr').find('.filter_value input');                
                var select_el = original_input.parent().find('select');
                if (element.val() == 'isnull')
                {
                   if (!select_el.length)
                   {
                      select_el = $('<select></select>').attr({name: original_input.attr('name')});
                      var true_opt = $('<option></option>').val("true").html('True')
                      var false_opt =  $('<option></option>').val("false").html('False');
                      if (original_input.val() == 'false')
                      {
                        false_opt.attr({ selected: "selected" });  
                      }
                      true_opt.attr({ selected: "selected" });
                      select_el.append(true_opt);
                      select_el.append(false_opt);                      
                      original_input.parent().append(select_el);                     
                   }                    
                   original_input.hide();                                      
                   select_el.show();
                }
                else
                {
                  original_input.show();
                  select_el.hide();                  
                }
            }
            initTriggers();
        });
    }
    $(document).ready( function () {
        Collection = $("#collection_form").CollectionForm();
    });
})(jQuery);

