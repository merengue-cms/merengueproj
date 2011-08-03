from django.utils.datastructures import SortedDict

from autoreports.utils import get_field_from_model, get_adaptor, get_ordered_fields


def get_fields(search):
    model = search.content_type.model_class()
    fields_form_filter = SortedDict({})
    fields_form_display = SortedDict({})

    ordered_fields = get_ordered_fields(search)
    for field_name, opts in ordered_fields:
        model_field, field = get_field_from_model(model, field_name)
        adaptor = get_adaptor(field)(model_field, field, field_name)
        adaptor.get_field_form(opts, default=True,
                                fields_form_filter=fields_form_filter,
                                fields_form_display=fields_form_display)
    return fields_form_filter
