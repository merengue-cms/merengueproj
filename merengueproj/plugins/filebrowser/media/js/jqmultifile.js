
(function ($) {

  var MultiSelector = function (input_list, max) {
    this.elem = input_list;
    this.max = max;
    this.count = 0;
    this.template = $('#multiselector-template');
  };

  MultiSelector.prototype.new_input = function () {
    $('.file_element').unbind();
    new_row = $(this.template.clone());
    new_row.attr('id', 'multiselector-row-' + this.count);
    new_row.attr('class', 'multiselector-row');
    title = 'title_' + this.count;
    title_label = $($(new_row.children()[0]).children()[0]);
    title_label.attr('for', title);
    title_input = $($(new_row.children()[0]).children()[1]);
    title_input.attr('id', title);
    title_input.attr('name', title);
    desc = 'description_' + this.count;
    desc_label = $($(new_row.children()[1]).children()[0]);
    desc_label.attr('for', desc);
    desc_input = $($(new_row.children()[1]).children()[1]);
    desc_input.attr('id', desc);
    desc_input.attr('name', desc);
    file = 'file_' + this.count;
    file_label = $($(new_row.children()[2]).children()[0]);
    file_label.attr('for', file);
    file_input = $($(new_row.children()[2]).children()[1]);
    file_input.attr('id', file);
    file_input.attr('name', file);
    this.count++;
    this.elem.append(new_row);
    new_row.show();
  };

  $(document).ready(function () {
    window.multiselector = new MultiSelector($('#file-set'), 20);
    window.multiselector.new_input();
    var new_file = $('#new-file');
    new_file.click(function (e) {
      window.multiselector.new_input();
      return false;
    });
  });

})(jQuery);
