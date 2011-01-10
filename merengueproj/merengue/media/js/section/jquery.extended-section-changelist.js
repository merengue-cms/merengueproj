(function($) {
    $.fn.SectionChangeList = function () {
        return this.each(function () {
            var changelist = $(this);
            var configuration = {};
            var sections = null;
            var tools = null;

            var readConfiguration = function() {
                var container = changelist.parents('#content').find('.section-configuration');

                configuration = {
                    ajaxLoader: container.find('.ajax-loading'),
                    menuToggle: container.find('.tools-toggle'),
                    sectionTools: container.find('.section-tools')
                };
                return configuration;
            }

            var initTools = function() {
                tools = configuration.sectionTools.find('li.tool');
                if (!tools.length) {
                    return false;
                }
                sections = changelist.find('table tbody tr');
                sections.each(function(i, e) {
                    var title = $(e).find('th a');
                    title.before(configuration.menuToggle.clone());
                    title.after('<div class="section-contents hide"></div>');
                    var contents = $(e).find('.section-contents');
                    contents.append(configuration.sectionTools.clone());
                    contents.find('.tool').each(function(j, d) {
                        if ($(e).hasClass('row1')) {
                            $(d).addClass('row' + ((j+1)%2+1));
                        } else {
                            $(d).addClass('row' + (j%2+1));
                        }
                        var tool_name = $(d).find('.tool-name').text();
                        var link = $(d).find('a.tool-main-link');
                        link.attr('href', title.attr('href') + tool_name + '/');
                    });
                });
                changelist.find('.tools-toggle').bind('click', toggleSectionTools);
                changelist.find('.contents-toggle').bind('click', toggleSectionContents);
            }

            var toggleSectionTools = function() {
                var toggle = $(this);
                var section = toggle.parents('tr').eq(0);
                toggle.find('img').toggleClass('hide');
                section.find('.section-contents').toggleClass('hide');
            }

            var toggleSectionContents = function() {
                var toggle = $(this);
                var tool = toggle.parents('li.tool').eq(0);
                var section = toggle.parents('tr').eq(0);
                toggle.find('img').toggleClass('hide');
                var contents = tool.find('.contents');
                if (!contents.length) {
                    firstContentQuery(section, tool);
                } else {
                    contents.toggleClass('hide');
                }
            };

            var firstContentQuery = function(section, tool) {
                tool.find('.tool-main-link').after(configuration.ajaxLoader.clone()); 
                tool.append('<div class="contents toolContentContainer"></div>');
                var contents = tool.find('.contents');
                var title = section.find('th a');
                var tool_name = tool.find('.tool-name').text();
                var url = title.attr('href') + tool_name + '/ajax/';
                $.ajax({
                    url: url,
                    type: 'GET',
                    cache: false,
                    async: true,
                    dataType: 'json',
                    success: function(response){
                        tool.find('.ajax-loading').remove();
                        contents.html('<ul class="toolContentList"></ul>');
                        var ul = contents.find('ul');
                        var add = tool.hasClass('row1')?0:1;
                        if(!response.size) {
                            tool.find('.tool-main-link').after('<span class="nocontents">' + response.message + '</span>');
                            ul.hide().removeClass("toolContentList");
                        } else {
                            $.each(response.contents, function(i, o) {
                                ul.append('<li class="row' + ((i+1+add)%2+1) +'"><a href="' + o.url + '">' + o.name + '</a></li>');
                            });
                        }
                    }
                });
            };

            var initChangeList = function() { 
                configuration = readConfiguration();
                initTools();
            }

            initChangeList();
        });
    };

    $(document).ready(function(){
        $('#changelist').SectionChangeList();
    });
})(jQuery);
