function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      if (oldonload) {
        oldonload();
      }
      func();
    }
  }
}

var AUTO_CHANGED = false;
addLoadEvent(function() {
    date0 = $("#id_publish_date_0");
    date1 = $("#id_publish_date_1");

    $("#id_status").change(function() {

        if ($(this).val() == 'published')
        {
            if (date0.val() == "" && date1.val() == "")
            {
                date0.val(DateTimeShortcuts.handleCalendarQuickLink(0, 0));
                date1.val(DateTimeShortcuts.handleClockQuicklink(0, new Date().getHourMinuteSecond()));
                AUTO_CHANGED = true;
            }
        }
        else
        {
            if (AUTO_CHANGED)
            {
                date0.val("");
                date1.val("");
            }
        }
    });
    date0.change(function () { AUTO_CHANGED = false; });
    date1.change(function () { AUTO_CHANGED = false; });
});
