/**
 * $RCSfile: editor_plugin_src.js,v $
 * $Revision: 0.01 $
 * $Date: 2008/10/20 09:29:39 $
 *
 * @author Yaco Sistemas S.L.
 * @copyright Copyright © 2008, Yaco Sistemas S.L., All rights reserved.
 */

/* Import plugin specific language pack */
tinyMCE.importPluginLanguagePack('contentindex', 'en,tr,cs,el,fr_ca,it,ko,sv,zh_cn,fa,fr,de,pl,pt_br,nl,da,he,nb,ru,ru_KOI8-R,ru_UTF-8,nn,fi,es,cy,is,pl');

var TinyMCE_ContentIndexPlugin = {
	getInfo : function() {
		return {
			longname : 'Insert headers for content index',
			author : 'Yaco Sistemas S.L.',
			authorurl : 'http://www.yaco.es',
			infourl : 'http://www.yaco.es',
			version : tinyMCE.majorVersion + "." + tinyMCE.minorVersion
		};
	},

	/**
	 * Returns the HTML contents of the contentindex control.
	 */
	getControlHTML : function(cn) {
		switch (cn) {
			case "section1":
				return tinyMCE.getButtonHTML(cn, 'lang_insertdate_desc', '{$pluginurl}/images/insertdate.gif', 'mceContentIndexS1');
			case "section2":
				return tinyMCE.getButtonHTML(cn, 'lang_insertdate_desc', '{$pluginurl}/images/insertdate.gif', 'mceContentIndexS2');
			case "section3":
				return tinyMCE.getButtonHTML(cn, 'lang_insertdate_desc', '{$pluginurl}/images/insertdate.gif', 'mceContentIndexS3');
			case "section4":
				return tinyMCE.getButtonHTML(cn, 'lang_insertdate_desc', '{$pluginurl}/images/insertdate.gif', 'mceContentIndexS4');
		}

		return "";
	},

	/**
	 * Executes the mceContentIndex command.
	 */
	execCommand : function(editor_id, element, command, user_interface, value) {

		function insertH1() {
			var selected_html = tinyMCE.getInstanceById(editor_id).selection.getSelectedHTML();
			return "<h1 class=\"Section1\">" + selected_html + "</h1>";
		}

		function insertH2() {
			var selected_html = tinyMCE.getInstanceById(editor_id).selection.getSelectedHTML();
			return "<h2 class=\"Section2\">" + selected_html + "</h2>";
		}

		function insertH3() {
			var selected_html = tinyMCE.getInstanceById(editor_id).selection.getSelectedHTML();
			return "<h3 class=\"Section3\">" + selected_html + "</h3>";
		}

		function insertH4() {
			var selected_html = tinyMCE.getInstanceById(editor_id).selection.getSelectedHTML();
			return "<h4 class=\"Section4\">" + selected_html + "</h4>";
		}

		// Handle commands
		switch (command) {
			case "mceContentIndexS1":
				tinyMCE.execInstanceCommand(editor_id, 'mceInsertContent', false, insertH1());
				return true;
			case "mceContentIndexS2":
				tinyMCE.execInstanceCommand(editor_id, 'mceInsertContent', false, insertH2());
				return true;
			case "mceContentIndexS3":
				tinyMCE.execInstanceCommand(editor_id, 'mceInsertContent', false, insertH3());
				return true;
			case "mceContentIndexS4":
				tinyMCE.execInstanceCommand(editor_id, 'mceInsertContent', false, insertH4());
				return true;
		}

		// Pass to next handler in chain
		return false;
	}
};

tinyMCE.addPlugin("contentindex", TinyMCE_ContentIndexPlugin);
