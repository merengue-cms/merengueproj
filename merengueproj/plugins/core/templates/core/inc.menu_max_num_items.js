{% load i18n %}

var classPattern = "menuDepth";

function getCollapsableMenu(menu) {
    var maxNumItems,
        maxNumLevel,
        menuItems,
        menuItemsLength,
        excludeMenuItems,
        excludeMenuItemsCurrent,
        itemSelected,
        firstDepth,
        currentDepth,
        i, j;
    menuItems = menu.find("li");
    menuItemsLength = menuItems.length;
    maxNumItems = {{ max_num_items }};
    maxNumLevel = {{ max_num_level }};
    excludeMenuItems = [];
    if (menuItemsLength > maxNumItems) {
        currentDepth = null;
        itemSelected = menu.find("li.selected");
        if (itemSelected.length == 0) {
            currentDepth = 2;
        } else {
            currentDepth = getDepthOfItem(itemSelected);
        }
        firstDepth = getDepthOfItem(menu.find("ul:first li"));
        lastDepth = firstDepth + maxNumLevel -1;
        i = lastDepth;
        while (menuItemsLength > maxNumItems && i >= currentDepth ) {
            excludeMenuItemsCurrent = menu.find("ul." + classPattern + i).not(
                                                itemSelected.parents()).not(
                                                itemSelected.find("ul"));
            if (excludeMenuItemsCurrent.length > 0) {
                excludeMenuItemsCurrent.map(function(i, elem){
                    excludeMenuItems[excludeMenuItems.length] = $(elem);
                })
                menuItemsLength -= excludeMenuItemsCurrent.find("li").length;
            }
            i --;
        }

        for (j=0; j < excludeMenuItems.length; j++) {
            excludeMenuItems[j].slideToggle();
            var altCollapsable = '{% trans "Collapsable" %}';
            iconElementCollapsable = jQuery('<a href="#" class="collapsable"' + ' alt="'+ altCollapsable +'" title="'+ altCollapsable +'">&nbsp;</a>');
            excludeMenuItems[j].parent().addClass('extensibleMenu');
            iconElementCollapsable.insertBefore(excludeMenuItems[j].parent().find("a.item:first"));
            iconElementCollapsable.fadeOut();

            iconElementCollapsable.click(function(){
                $(this).fadeOut();
                $(this).parent().find("a.extensible").fadeIn();
                $(this).parent().find("ul:first").slideToggle();
                return false;
            });

            var altExtensible = '{% trans "Extensible" %}';
            iconElementExtensible = jQuery('<a href="#" class="extensible"' + ' alt="'+ altExtensible +'" title="'+ altExtensible +'">&nbsp;</a>');
            iconElementExtensible.insertBefore(excludeMenuItems[j].parent().find("a.item:first"));

            iconElementExtensible.click(function(){
                $(this).fadeOut();
                $(this).parent().find("a.collapsable").fadeIn();
                $(this).parent().find("ul:first").slideToggle();
                return false;
            });
        }
    }
}

function getDepthOfItem(itemSelected) {
    var i,
        classes,
        classPatternLength,
        currentDepth;
    currentDepth = null;
    classes = itemSelected.parent().attr("class").split(" ").reverse();
    i = 0;
    classPatternLength = classPattern.length;
    while(!currentDepth || i < classes.length) {
        if (classes[i].substring(0, classPatternLength) == "menuDepth") {
            currentDepth = classes[i].substring(classPatternLength);
        }
        i++;
    }
    return parseInt(currentDepth);
}