var $j = jQuery.noConflict();

function showForm(form_id) {
  $j('#'+form_id + 'form').css('display', 'block');
  $j('#'+form_id + 'btn').css('display', 'none');
  $j('#'+form_id).focus();
  return false;
}
function hideForm(form_id) {
  $(form_id + 'form').style.display = 'none';
  $(form_id + 'btn').style.display = 'block';
  return false;
}

function removeAttachment(remove_url, type, objId) {
  /* Remove it from the server */
  $j("#removeattachmentform").ajaxForm({
    type: "POST",
    url: remove_url,
    dataType: "json",
    data: {'test': 1},
    success: function(json) {
            if (json.success) {
                    $j("#"+type + "-" + objId).remove();
                    }
        },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert('Server error: ' + textStatus);
        },
   });
  $j("#removeattachmentform").submit()
}
