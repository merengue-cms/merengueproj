function insertLink(link_url, title_url) {
	var ed = tinyMCEPopup.editor, e, b;

	tinyMCEPopup.restoreSelection();
	e = ed.dom.getParent(ed.selection.getNode(), 'A');

	tinyMCEPopup.execCommand("mceBeginUndoLevel");

	// Create new anchor elements
	if (e == null) {
		ed.getDoc().execCommand("unlink", false, null);
		tinyMCEPopup.execCommand("CreateLink", false, "#mce_temp_url#", {skip_undo : 1});

		tinymce.each(ed.dom.select("a"), function(n) {
			if (ed.dom.getAttrib(n, 'href') == '#mce_temp_url#') {
				e = n;

				ed.dom.setAttribs(e, {
					href : link_url,
					title : title_url,
				});
			}
		});
	} else {
		ed.dom.setAttribs(e, {
			href : link_url,
			title : title_url,
		});
	}

	// Don't move caret if selection was image
	if (e.childNodes.length != 1 || e.firstChild.nodeName != 'IMG') {
		ed.focus();
		ed.selection.select(e);
		ed.selection.collapse(0);
		tinyMCEPopup.storeSelection();
	}

	tinyMCEPopup.execCommand("mceEndUndoLevel");
	tinyMCEPopup.close();
}
