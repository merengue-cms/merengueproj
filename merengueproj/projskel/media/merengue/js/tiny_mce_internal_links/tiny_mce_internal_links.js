var TinyMCE_InternalLinksPlugin = {
	getInfo : function() {
		return {
			longname : 'Internal Links Plugin',
			author : 'Yaco',
			authorurl : 'http://www.yaco.es',
			infourl : 'http://www.yaco.es',
			version : tinyMCE.majorVersion + "." + tinyMCE.minorVersion
		};
	},

	/**
	 * Returns the HTML contents of the preview control.
	 */
	getControlHTML : function(cn) {
		switch (cn) {
			case "internal_links":
				return tinyMCE.getButtonHTML(cn, 'lang_internal_links_desc', '{$pluginurl}/images/internal_link.gif', 'mceInternalLink');
		}

		return "";
	},

	/**
	 * Executes the mceInternalLink command.
	 */
	execCommand : function(editor_id, element, command, user_interface, value) {
		// Handle commands
		switch (command) {
			case "mceInternalLink":
				var internalLinksURL = tinyMCE.getParam("plugin_internal_links_url", null);
				var internalLinksWidth = tinyMCE.getParam("plugin_internal_links_width", "850");
				var internalLinksHeight = tinyMCE.getParam("plugin_internal_links_height", "600");

				// Use a custom preview page
				if (internalLinksURL) {
					var template = new Array();

					template['file'] = internalLinksURL;
					template['width'] = internalLinksWidth;
					template['height'] = internalLinksHeight;

					tinyMCE.openWindow(template, {editor_id : editor_id, resizable : "yes", scrollbars : "yes", inline : "yes", content : tinyMCE.getContent(), content_css : tinyMCE.getParam("content_css")});
				}

				return true;
		}

		return false;
	},
	
        handleNodeChange : function(editor_id, node, undo_index, undo_levels, visual_aid, any_selection) {
                if (node == null)
                        return;

                do {
                        if (node.nodeName == "A" && tinyMCE.getAttrib(node, 'href') != "") {
                                tinyMCE.switchClass(editor_id + '_internal_links', 'mceButtonSelected');
                                return true;
                        }
                } while ((node = node.parentNode));

                if (any_selection) {
                        tinyMCE.switchClass(editor_id + '_internal_links', 'mceButtonNormal');
                        return true;
                }

                tinyMCE.switchClass(editor_id + '_internal_links', 'mceButtonDisabled');

                return true;
        }

};

(function($) {
    $(document).ready(function () {
        tinyMCE.addPlugin('internal_links', TinyMCE_InternalLinksPlugin);
        tinyMCE.setPluginBaseURL("internal_links", "/media/merengue/js/tiny_mce_internal_links");
	tinyMCE.addToLang('internal_links',{
		desc : 'Insert internal link'
	});
    });
})(jQuery);
