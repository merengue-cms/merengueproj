function TinyImagesFileBrowser(field_name, url, type, win) {

    var baseURL = tinyMCE.selectedInstance.settings['tiny_images_base_url'] || '/tinyimages/';
    var cmsURL = baseURL + type + "/";
    
    tinyMCE.selectedInstance.windowManager.open({
        url: cmsURL,
        width: 600,  // Your dimensions may differ - toy around with them!
        height: 560,
        resizable: "yes",
        scrollbars: "yes",
        inline: "no",  // This parameter only has an effect if you use the inlinepopups plugin!
        close_previous: "no",
        field_name: field_name,
        win: win
    });
    return false;
}

function update_field(field, value) {
    if (field) field.value=value;
}

function returnURL(url, alt, width, height) {
	var win = tinyMCEPopup.features['win']

	win.document.getElementById(tinyMCEPopup.features['field_name']).value = url;
	update_field(win.document.getElementById("alt"), alt);
	update_field(win.document.getElementById("linktitle"), alt);
	update_field(win.document.getElementById("width"), width);
	update_field(win.document.getElementById("height"), height);
	tinyMCEPopup.close();
}
