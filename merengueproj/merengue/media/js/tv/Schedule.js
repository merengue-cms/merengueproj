(function ($) {

    $.fn.WeekSchedule = function () {
        return this.each(function () {
            var table = $(this).find('table');
            var schedule = $('.schedule-week-view table');
            var weekdayindex = null;
            var startsecondsindex = null;
            var endsecondsindex = null;
            var delta = parseInt($('#hoursdelta').text());
	    var reduced = false;

            var createDiv = function(link) {
                $('body').prepend('<div class="videoAccess">' + link + '</div>');
                var newdiv = $('body').children().eq(0);
                if (reduced) {
                    newdiv.addClass('videoAccessReduced');
                    newdiv.insertAfter($('.schedule-week-view'));
                }
                return newdiv;
            }

            var calculateTop = function(td, start, init_seconds) {
                var ref = (start - init_seconds) / delta;
                var result = td.offset().top + (td.height() * ref);
                return result;
            }


            var calculateHeight = function(td, start, end) {
                var ref = td.height() / delta;
                return (end - start) * ref;
            }

            var place = function(link, weekday, startseconds, endseconds) {
                var init_td = null;
                var end_td = null;
                var init_seconds = null;
                var end_seconds = null;

                var start = parseInt(startseconds);
                var end = parseInt(endseconds);
                var day = parseInt(weekday);

                schedule.find('thead tr th').each(function(i, o) {
                    if ($(this).hasClass('day-' + day)) {
                        day = i;
                        return false;
                    }
                });

                schedule.find('tbody tr span.hour-init-seconds').each(function(i, o) {
                    var seconds = parseInt($(this).text());
                    if (seconds <= start) {
                        init_td = $(this);
                        init_seconds = seconds;
                    } 
                    if (seconds <= end) {
                        end_td = $(this);
                        end_seconds = seconds;
                    } else if (seconds > end) {
                        return false;
                    }
                });
	        init_td = init_td.parents('tr').children().eq(day);
	        end_td = end_td.parents('tr').children().eq(day);
                var newdiv = createDiv(link);
                newdiv.css('left', init_td.offset().left);
                newdiv.css('top', calculateTop(init_td, start, init_seconds));
                newdiv.css('width', init_td.css('width'));
                newdiv.css('height', calculateHeight(end_td, start, end));
            }

            var insertScheduleRow = function(row) {
                var weekday = row.children().eq(weekdayindex).text();
                var startseconds = row.children().eq(startsecondsindex).text();
                var endseconds = row.children().eq(endsecondsindex).text();
                var link = row.find('th').html();

                place(link, weekday, startseconds, endseconds);
            }

            var setIndexes = function() {
                table.find('thead th').each(function(i, o) {
                    if ($(this).text().match(/\W*Weekday\W*/)) {
                        weekdayindex = i;
                    } else if ($(this).text().match(/\W*Start seconds\W*/)) {
                        startsecondsindex = i;
                    } else if ($(this).text().match(/\W*End seconds\W*/)) {
                        endsecondsindex = i;
                    }
                });
            }

            var fillWeek = function() {
                setIndexes();

                table.find('tbody tr').each(function() {
                    insertScheduleRow($(this));
                });
            }

            var videoAccessEfects = function() {
                $(".videoAccess").bind('mouseenter', function() {
                    var child_height = $(this).children().eq(0).height();
                    var child_width = $(this).children().eq(0).width();
                    var table = $('.schedule-week-view table');
                    var border = table.offset().left + table.width();
                    $(this).data('old_height', $(this).height());
                    $(this).data('old_width', $(this).width());
                    $(this).data('old_left', $(this).offset().left);
                    if (child_height > $(this).height()) {
                        $(this).css('height', child_height);
                    }
                    if (child_width > $(this).width()) {
                        $(this).css('width', child_width);
                    }
                    if ($(this).width() + $(this).offset().left > border) {
                        $(this).css('left', border - $(this).width());
                    }
                }).bind('mouseleave', function() {
                    $(this).css('height', $(this).data('old_height'));
                    $(this).css('width', $(this).data('old_width'));
                    $(this).css('left', $(this).data('old_left'));
                });
            }

            var moveObjectTools = function() {
                $('.object-tools').insertBefore('.filter-date');
            }

            $(this).hide();
            reduced = $('.set-reduced-view').length;
            fillWeek();
            moveObjectTools();
            if (reduced) {
                $('.schedule-week-view').hide();
            } else {
                videoAccessEfects();
            }
        });
    }

    $(document).ready(function () {
        $("#changelist").WeekSchedule();
    });

})(jQuery);
