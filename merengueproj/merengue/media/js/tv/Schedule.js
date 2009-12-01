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
                newdiv.data('parenttd', init_td);
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

            var setDragAndDrop = function() {
                $('.videoAccess').draggable({
                    tolerance: 'pointer',
                    delay: 500,
                    revert: 'invalid',
                    cursorAt: { left: 5,
                                top: 5 }
                });
                $('.schedule-week-view tbody td.schedule').droppable({
                    accept: '.videoAccess',
                    hoverClass: 'tddroppable',
                    tolerance: 'pointer',
                    drop: function(event, ui) {
                        var old_left = ui.draggable.data('old_left');
                        var old_top = ui.draggable.data('old_top');
                        $.ajax({
                            url: window.location.href,
                            type: "GET",
                            async: true,
                            data: { date: $(this).find('.td_datetime').html(),
                                    schedule_id: ui.draggable.find('.schedule_id').html()
                                  },
                            dataType: 'json',
                            success: function(response){
                                ui.draggable.find('.video-start').html(response.start_date);
                                ui.draggable.find('.video-end').html(response.end_date);
                            },
                            error: function(response){
                                ui.draggable.data('old_left', old_left);
                                ui.draggable.data('old_top', old_top);
                                ui.draggable.css('left', old_left);
                                ui.draggable.css('top', old_top);
                                collapseSchedule(ui.draggable);
                        }});
                        ui.draggable.data('old_left', $(this).offset().left);
                        ui.draggable.data('old_top', $(this).offset().top);
                        ui.draggable.css('left', $(this).offset().left);
                        ui.draggable.css('top', $(this).offset().top);
                    }
                });
            }

            var expandSchedule = function(schedule) {
                if (!schedule.data('keep')) {
                    var child_height = schedule.children().eq(0).height();
                    var child_width = schedule.children().eq(0).width();
                    var table = $('.schedule-week-view table');
                    var border = table.offset().left + table.width();
                    schedule.data('old_height', schedule.height());
                    schedule.data('old_width', schedule.width());
                    schedule.data('old_left', schedule.offset().left);
                    schedule.data('old_top', schedule.offset().top);
                    schedule.data('keep', false);
                    if (child_height > schedule.height()) {
                        schedule.css('height', child_height);
                    }
                    if (child_width > schedule.width()) {
                        schedule.css('width', child_width);
                    }
                    if (schedule.width() + schedule.offset().left > border) {
                        schedule.css('left', border - schedule.width());
                    }
                    schedule.css('z-index', '99999');
                }
            }

            var collapseSchedule = function(schedule) {
                if (!schedule.data('keep')) {
                    schedule.css('height', schedule.data('old_height'));
                    schedule.css('width', schedule.data('old_width'));
                    schedule.css('left', schedule.data('old_left'));
                    schedule.css('top', schedule.data('old_top'));
                    schedule.css('z-index', '1');
                }
            }

            var videoAccessEfects = function() {
                $(".videoAccess").bind('mouseenter', function() {
                    expandSchedule($(this));
                }).bind('mouseleave', function() {
                    collapseSchedule($(this));
                }).bind('mousedown', function() {
                    $(this).data('keep', true);
                }).bind('mouseup', function() {
                    $(this).data('keep', false);
                });
                setDragAndDrop();
            }

            var moveObjectTools = function() {
                $('.object-tools').insertBefore('.filter-date');
            }

            $(this).hide();
            moveObjectTools();
            reduced = $('.set-reduced-view').length;
            fillWeek();
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
