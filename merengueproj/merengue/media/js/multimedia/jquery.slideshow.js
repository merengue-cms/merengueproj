(function($) {
    $.fn.MultimediaSlideShow = function () {
        return this.each(function () {
            var slide = $(this);
            var menu = $(this).find('.MultimediaSlideActionLinks');
            var display = $(this).find('.MultimediaSlideVisualZone');
            var paginator = $(this).find('.imageController');
            var types = {};
            var current = null;
            var mediaurl;
            var typeorder;

            var initShadowBox = function() {
                Shadowbox.init({
                    assetUrl: mediaurl,
                    loadingImage: mediaurl + 'multimedia/img/loading.gif',
                    displayNav: true,
                    displayClose: true,
                    skipSetup: true,
                    continuous: true,
                    enableKeys: false
                });
            }

            var configureShadowBox = function() {
                Shadowbox.setup(slide.find('.MultimediaItemThumbnail a'), {
                    flvPlayer: mediaurl + 'merengue/flash/flowplayer-3.2.7.swf'
                });
            }

            var configureStreetViewShadowBox = function() {
                Shadowbox.setup($('.street_view_shadowlink'), {});
                menu.find('.toStreet').appendTo(menu).bind('full-show', function() {
                   $(this).parents('.MultimediaSlide').show();
                });
            }

            var configureSlide = function() {
                mediaurl = slide.find('.MultimediaConfigurationMediaURL').text();
                typeorder = slide.find('.MultimediaConfigurationActionLinksOrder').text();
                typeorder = typeorder.split(" ");
            };

            var initSlide = function() { 
	        configureSlide();
                initShadowBox();
                if ($('.MultimediaItemThumbnail a').length) {
                    configureShadowBox();
                    findMultimediaTypes();
                    showTypes();
                    bindActionLinks();
                    bindPaginationLinks();
                    setFirstType();
                    slide.show();
                } else {
                    paginator.hide();
                }
                configureStreetViewShadowBox();
            }

            var addNewType = function (typename) {
                if (typeof(types[typename]) != 'undefined')
                    return;
                types[typename]={'items': new Array(),
                                 'current_item': 0
                                };
            };

            var getType = function(typename) {
                if (typeof(types[typename]) != 'undefined')
                    return types[typename];
	        return null;
            };

            var addNewItem = function(typename, item) {
                type = getType(typename);
                type.items.push(item);
                if ($(item).find('.MultimediaItemThumbnail a').attr('rel').indexOf('video')>=0) {
                    $(item).find('.MultimediaItemThumbnail a').append('<span class="playbutton">&nbsp;</span>');
                }
            };

            var findMultimediaTypes = function() {
                slide.find('.MultimediaItemClass').each(function() {
                    addNewType($(this).text());
                    addNewItem($(this).text(), $(this).parent('.MultimediaItem'));
                });
            };

            var showTypes = function() {
                var count = 0;
                $.each(typeorder, function(index, t) {
                    if (typeof(types[t]) != 'undefined') {
                        menu.append('<span class="galleryButton galleryButton-'+ t +'"><img src="' + mediaurl + 'merengue/img/multimedia/mediacontents/' + t + '_action_link.png" /></span>')
                        types[t].order=index;
                        count += types[t].items.length;
                    }
                });
                if (count <= 1) {
                    slide.addClass('withoutMenu');
                }
            };

            var showItem = function(item) {
                display.find('.MultimediaItem').stop(false, true);
                var visible = display.find('.MultimediaItem:visible');
                if (visible.length) {
                    visible.fadeOut('slow', function() {
                        $(item).fadeIn().show();
                    });
                } else {
                    $(item).fadeIn().show();
                }
            };

            var setCurrentPagination = function(value) {
                paginator.find('.imgNow').text(value+1);
            }

            var setMaxPagination = function(value) {
                paginator.find('.imgMax').text(value);
                if (value==1) {
                    paginator.hide();
                } else {
                    paginator.show();
                }
            }

            var activateType = function(type, action_link) {
                if (current!=type) {
                    setMaxPagination(type.items.length);
                    setCurrentPagination(type.current_item);
                    showItem(type.items[type.current_item]);
                    if (current)
                        returnToPosition(current);
                    menu.prepend(action_link);
                    menu.find('.activeButton').removeClass('activeButton');
                    action_link.addClass('activeButton');
                    current = type;  
                }
            };

            var returnToPosition = function(type) {
                if (!type.order) return;
                var first = menu.find('.galleryButton').eq(0);
                menu.find('.galleryButton').eq(type.order).after(first);
            };

            var bindActionLinks = function() {
                $.each(types, function(key, value) {
                    menu.find('.galleryButton-'+ key).click(function() {
                        activateType(value, $(this));
                    });
                });
            };

            var getCurrentItem = function(type) {
                return type.items[type.current_item];
            };

            var bindPaginationLinks = function() {
                paginator.find('.prevImg').click(function () {
                    if (current.current_item<=0)
                        return false;
                    current.current_item -= 1;
                    showItem(getCurrentItem(current));
                    setCurrentPagination(current.current_item);
                });
                paginator.find('.nextImg').click(function () {
                    if (current.current_item>=current.items.length-1)
                        return false;
                    current.current_item += 1;
                    showItem(getCurrentItem(current));
                    setCurrentPagination(current.current_item);
                });
            };

            var setFirstType = function() {
                menu.find('.galleryButton:visible').eq(0).click();
            };

            initSlide();
        });
    };

    $(document).ready(function(){
        $('.MultimediaSlide').MultimediaSlideShow();
    });
})(jQuery);
