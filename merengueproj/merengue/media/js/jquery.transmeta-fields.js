(function($) {
    $.fn.FieldSet = function () {
        return this.each(function () {
            var fieldset = $(this);
            var parsed = {};
            var editors = {};

            var includeIntoField = function(row, pitem) {
                pitem['fields'].push(row);
            };

            var addNewField = function(row, canonical) {
                parsed[canonical]={}
                parsed[canonical]['fields']=[]
                includeIntoField(row, parsed[canonical]);
            };

            var initFields = function() {
                fieldset.find('.field-meta').each(function() {
                    var meta = $(this);
                    var row = meta.parents('div.form-row');
                    var canonical = $(this).find('span.canonical').text();
                    if (typeof(parsed[canonical]) != 'undefined') {
                        includeIntoField(row, parsed[canonical]);
                    } else {
                        addNewField(row, canonical);
                    }
                });
            };

            var createField = function(container, field) {
                var labels = container.find('> .labels');
                var fields = container.find('> .fields');
                var label_tag = field.find('.label-tag');
                var field_content = field.find('.field-after-label');
                var label_for = label_tag.find('> label').attr('for');
                var help = field.find('.help');
                field_content.addClass(label_for);
                field_content.hide();
                labels.append(label_tag);
                fields.prepend(field_content);
                if (field.find('span.current').length) {
                    label_tag.addClass('active');
                    field_content.show();
                };
                if (field.hasClass('errors')) {
                    label_tag.addClass('errors');
                    var errorlist = field.find('.errorlist');
                    field_content.prepend(errorlist);
                    if (label_tag.hasClass('active')) {
                        fields.addClass('errors');
                    }
                };
                help.addClass('translatable');
                field_content.append(help);
            };

            var redoFields = function() {
                $.each(parsed, function(index, value) {
                    var first=null;
                    var container=null;
                    var labels=null;
                    var fields=null;
                    $.each(value['fields'], function(i, field) {
                        field.find('script').remove();
                        if (!first) {
                            first=field;
                            field.wrap('<div class="trans-field-container"></div>');
                            container=field.parent('.trans-field-container');
                            container.prepend('<div class="fields"><br style="clear: left;" /></div>');
                            container.prepend('<div class="labels"></div>');
                            createField(container, field)
                        } else {
                            container.append(field);
                            createField(container, field)
                        }
                    });
                });
            };

            var changeTab = function() {
                var tab=$(this).parent('.label-tag');
                var labels=tab.parent('.labels');
                labels.find('.label-tag').removeClass('active');
                tab.addClass('active');
                var field_id = $(this).attr('for');
                var field = tab.parents('.trans-field-container').find('.' + field_id).eq(0);
                var fields = field.parent('.fields');
                fields.find('.field-after-label').hide();
                field.show();
                if (tab.hasClass('errors')) {
                    fields.addClass('errors');
                } else {
                    fields.removeClass('errors');
                }
            };

            var initTriggers = function() {
                $('.trans-field-container label').click(changeTab);
            };

            initFields();
            redoFields();
            initTriggers();
        });
    };

    $(document).ready(function(){
        $('fieldset.module').FieldSet();
    });
})(jQuery);
