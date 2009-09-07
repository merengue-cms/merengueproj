(function ($) {
    var plus = '<img class="plusMenu" src="/media/merengue/img/section/admin/plus.gif" /><img class="minusMenu hide" src="/media/merengue/img/section/admin/minus.gif" />';
    var span15 = '<span class="span15">&nbsp;</span>';
    var span50 = '<span class="span50">&nbsp;</span>';

    function show_submenus(menu) {
        var level = menu.data('level');
        menu.nextAll("tr").each(function() {
            next_level = $(this).data('level');
            if (next_level <= level) {
                return false;
            } else if (next_level == level + 1) {
                $(this).show();
                menu.find(".minusMenu").show();
                menu.find(".plusMenu").hide();
            }
        });
    }

    function hide_submenus(menu) {
        level = menu.data('level');
        menu.nextAll("tr").each(function() {
            next_level = $(this).data('level');
            if (next_level <= level) {
                return false;
            } else {
                $(this).hide();
                $(this).find(".minusMenu").hide();
                $(this).find(".plusMenu").show();
            }
        });
    }

    function make_level() {
        var menu = $(this);
        var level = $(this).data('level');
        var next_level = $(this).next('tr').eq(0).data('level');
        if (level!=1) {
            menu.hide();
        }
       
        if (next_level) {
            if (next_level > level) {
                menu.children("th").eq(0).prepend(plus);
                menu.children("th").eq(0).css('white-space', 'nowrap');
                menu.children("th").eq(0).find('a').css('white-space', 'normal');
                menu.find(".plusMenu").click(function() {
                    $(this).hide();
                    show_submenus(menu);
                    $(this).next(".minusMenu").show();
                });
                menu.find(".minusMenu").click(function() {
                    $(this).hide();
                    hide_submenus(menu);
                    $(this).prev(".plusMenu").show();
                });
            } else {
                menu.children("th").eq(0).prepend(span15);
            }
        } else {
            menu.children("th").eq(0).prepend(span15);
        }

        for(var i=0;i<level-1;i++) {
            menu.children("th").eq(0).prepend(span50);
        }
    }

    function initMoveMenu() {
        row = $(this).parents("tr")
        row.addClass('selected-row');
        $("a.initMoveMenu").hide();
        $("ul.insertOptions").show();
        row.nextAll("tr").each(function() {
           if ($(this).data('level') <= row.data('level')) return false;
           $(this).find("ul.insertOptions").hide();
        });
        row.find("ul.insertOptions").hide();
        row.find("a.cancelMoveMenu").show();
    }

    function cancelMoveMenu() {
        row = $(this).parents("tr")
        row.removeClass('selected-row');
        $("a.initMoveMenu").show();
        $("ul.insertOptions").hide();
        $("a.cancelMoveMenu").hide();
    }

    function moveMenu(menu, movement) {
        source = $("tr.selected-row input.thisMenu").val();
        target = $(menu).parents("tr").find("input.thisMenu").val();
        window.location="?source=" + source + '&target=' + target + '&movement=' + movement
    }

    function insertPrev() {
        moveMenu(this, 'left');
    }

    function insertNext() {
        moveMenu(this, 'right');
    }

    function insertChild() {
        moveMenu(this, 'first-child');
    }

    function bindMovementActions() {
        $("a.initMoveMenu").click(initMoveMenu);
        $("a.cancelMoveMenu").click(cancelMoveMenu);
        $("a.insertPrev").click(insertPrev);
        $("a.insertNext").click(insertNext);
        $("a.insertChild").click(insertChild);
    }

    function displayMovedMenu() {
        menu = $("span.movedSource").text();
        if (!menu) return;
        row = $("input.thisMenu[value="+menu+"]").parents("tr"); 
        row.prevAll("tr").each(function() {
            level = $(this).data('level');
            if (row.data('level') > level) {
                show_submenus($(this));
            }
            if (level == 0) {
                return False;
            }
        });
    }

    $(document).ready(function () {
        $("#changelist table thead tr").children("th").eq(0).remove();
        $("#changelist table tbody tr").each(function(i) {
            td_level = $(this).children("td").eq(0);
            level = parseInt(td_level.text());
            td_level.remove();
            $(this).data('level', level);
        });
        $("#changelist table tbody tr").each(make_level);
        bindMovementActions();
        displayMovedMenu();
    });

})(jQuery);
