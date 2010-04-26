function inplaceeditform_ready($){
    $('.inplace-view-editable-field').unbind('.inplaceEditForm');
    $('.inplace-view-editable-field').bind("mouseenter.inplaceEditForm",function(){
        $(this).addClass("edit_over");
    }).bind("mouseleave.inplaceEditForm",function(){
        $(this).removeClass("edit_over");
    });

    $('.inplace-view-editable-field').bind('dblclick.inplaceEditForm',function (){
        $(this).hide();
        var tools = $(this).next('.inplace-tools');
        tools.show();
        var tools_error = tools.find('.inplace-tools-error');
        tools_error.children().remove();
    });

    $('.inplace-tools .cancel').unbind('.inplaceEditForm');
    $('.inplace-tools .cancel').bind('click.inplaceEditForm', function (){
        var inplace_tools = $(this).parent();
        inplace_tools.hide();
        inplace_tools.prev('.inplace-view-editable-field').show();
    });

    $('.inplace-tools .apply').unbind('.inplaceEditForm');
    $('.inplace-tools .apply').bind('click.inplaceEditForm', function (){
        var _self = this;
        var auto_id = $(this).parent().find('.field_id').html();
        var field_name = $(this).parent().find('.field_name').html();
        var obj_id = $(this).parent().find('.obj_id').html();
        var content_type_id = $(this).parent().find('.content_type_id').html();
        var form = $(this).parent().find('.form').html();
        var filters = $.evalJSON($(this).parent().find('.filters').html());
        var value_input = $(this).parent().find('#' + auto_id);
        
        var value;
        if (value_input.attr('multiple'))
        {
            var options_selected = value_input.find('option:selected');
            value = [];
            $.each(options_selected, function (i, val) {
                value[i] = options_selected[i].value;
            });
        }
        else{
            value = value_input[0].value;
        }

        var form_query = '';
        if (form)
        {
            form_query = '&form='+form;
        }

        
        var data = 'id=' + obj_id + '&field=' + field_name + '&value=' + encodeURIComponent($.toJSON(value)) +
                   '&content_type_id=' + content_type_id+form_query + '&'+'filters=' + $.toJSON(filters);
        $.ajax({
            data: data,
            url: "/inplaceeditform/",
            type: "POST",
            async:true,
            dataType: 'json',
            success: function(response){
                if (response.errors)
                {   
                    var tools_error = $(_self).parent().find('.inplace-tools-error');
                    tools_error.children().remove();
                    var html = '<ul class="errors">';
                    
                    for (var error in response)
                    {
                        if (error != 'errors')
                        {
                            html += '<li>' ;
                            if ("'+field_name+'" == error)
                                html += response[error];
                            else
                                html += error+ ": " +response[error];
                            html += '</li>'
                        }
                    }
                    html += "</ul>"
                    tools_error.html(html);
                }
                else
                {
                    var inplace_tools = $(_self).parent();
                    inplace_tools.hide();
                    inplace_tools.prev('.inplace-view-editable-field').html(response.value)
                    inplace_tools.prev('.inplace-view-editable-field').show();
                    var inplace_messages = inplace_tools.prev().prev('.inplace-messages');    
                    inplace_messages.fadeIn();
                    window.setTimeout("jQuery('.inplace-messages').fadeOut()", 2000);
                }
            }
        });
    });
}
