(function() {
tinymce.create('tinymce.plugins.InternalLinksPlugin', {
	getInfo : function() {
		return {
			longname : 'Internal Links Plugin',
			author : 'Yaco',
			authorurl : 'http://www.yaco.es',
			infourl : 'http://www.yaco.es',
			version : tinyMCE.majorVersion + "." + tinyMCE.minorVersion
		};
	},

	init: function(ed, url) {
                var base_url = ed.getParam('plugin_internal_links_base_url', url)

                ed.addButton('internal_links',
                             {title : 'lang_internal_links_desc',
                              cmd : 'mceInternalLink',
                              image : base_url + 'images/internal_link.gif'});

                ed.onNodeChange.add(function(ed, cmd, n, co) {
                        var node = n;
                        if (node == null)
                                return;
        
                        do {
                                if (node.nodeName == "A" && ed.dom.getAttrib(node, 'href') != "") {
                                        cmd.setDisabled('internal_links', false);
                                        cmd.setActive('internal_links', true);
                                        return true;
                                }
                        } while ((node = node.parentNode));
        
                        if (!ed.selection.isCollapsed()) {
				cmd.setDisabled('internal_links', false);
                                return true;
                        }
        
			cmd.setActive('internal_links', false);
			cmd.setDisabled('internal_links', true);
        
                        return true;
                });

	        ed.addCommand('mceInternalLink', function() {
			var ed=tinyMCE.activeEditor;
		        var internalLinksURL = ed.getParam("plugin_internal_links_url", null);
		        var internalLinksWidth = ed.getParam("plugin_internal_links_width", "650");
		        var internalLinksHeight = ed.getParam("plugin_internal_links_height", "600");
      
		        // Use a custom preview page
		        if (internalLinksURL) {
				ed.windowManager.open({
					url : internalLinksURL,
					width : internalLinksWidth,
					height: internalLinksHeight,
					movable: true,
					scrollbars: true,
					inline: true
				});
		        }
		        return true;
	        });
        }
});

tinymce.PluginManager.add('internal_links', tinymce.plugins.InternalLinksPlugin);
})();
