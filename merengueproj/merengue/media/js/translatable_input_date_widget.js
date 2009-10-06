(function ($) {
    $(document).ready(function () {
        if (typeof(DateTimeShortcuts) != 'undefined') {
            DateTimeShortcuts.handleCalendarQuickLink = function(num, offset) {
                var d = new Date();
                d.setDate(d.getDate() + offset)
                DateTimeShortcuts.calendarInputs[num].value = getLocalDate(d);
                $(DateTimeShortcuts.calendarInputs[num]).keyup();
                DateTimeShortcuts.dismissCalendar(num);
            };
            DateTimeShortcuts.handleCalendarCallback = function(num) {
                return "function(y, m, d) { var d = new Date(y, m-1, d); DateTimeShortcuts.calendarInputs["+num+"].value = getLocalDate(d); document.getElementById(DateTimeShortcuts.calendarDivName1+"+num+").style.display='none';jQuery(DateTimeShortcuts.calendarInputs["+num+"]).keyup();}";
            };
        }

        $(".TranslatableInputDateWidget").keyup(function() {
            id=$(this).attr('id');
            hidden_id = id.replace('visual-','')
            $("#"+hidden_id).val(getISODateFromLocalDate($(this).val()));
        });


        $(".TranslatableInputDateWidget").each(function() {
            id=$(this).attr('id');
            hidden_id = id.replace('visual-','')
            hidden_value = $("#"+hidden_id).val()
            if (hidden_value) {
                year = hidden_value.split("-")[0];
                month = parseInt(hidden_value.split("-")[1])-1;
                day = hidden_value.split("-")[2];
		if (year && month && day)
                	$(this).val(getLocalDate(new Date(year, month, day)));
            }
        });
    });
})(jQuery);
