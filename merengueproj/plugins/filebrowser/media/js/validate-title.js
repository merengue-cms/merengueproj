
(function ($) {

  $(document).ready(function () {
    var button = $('input#rename-button');
    button.click(function (e) {
      e.preventDefault();
      var form = $('form#rename-form');
      var ok = true;
      var msg = '';
      $('input.title_element').each(function (index) {
        var value = $(this).val();
        if (!value) {
          ok = false;
          msg = $('span#translation-title-required').html();
          var border = $(this).css('border');
          $(this).css('border', 'solid orange');
          $(this).focus(function (e) {
            $(this).css('border', border);
          });
        }
      });
      $('input.file_element').each(function (index) {
        var value = $(this).val();
        if (!value) {
          ok = false;
          msg = $('span#translation-file-required').html();
          var border = $(this).css('border');
          $(this).css('border', 'solid orange');
          $(this).focus(function (e) {
            $(this).css('border', border);
          });
        }
      });
      if (ok) {
        form.submit();
      } else {
        alert(msg);
        return false;
      }
    });
  });

})(jQuery);
