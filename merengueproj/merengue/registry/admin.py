from merengue.base.admin import BaseOrderableAdmin, set_field_read_only
from merengue.registry import is_broken
from merengue.registry.models import RegisteredItem


class RegisteredItemAdmin(BaseOrderableAdmin):
    readonly_fields = ('class_name', 'module', 'category', )
    list_display = ('class_name', 'module', 'category', 'active', )
    list_filter = ('category', )
    change_form_template = 'admin/registry/change_form.html'
    sortablefield = 'order'

    def has_add_permission(self, request):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super(RegisteredItemAdmin, self).get_form(request, obj,
                                                         **kwargs)

        broken_item = is_broken(obj)

        if broken_item:
            # a broken registered item will be not editable by anybody
            for field_name, field in form.base_fields.items():
                set_field_read_only(field, field_name, obj)

        if not broken_item and 'config' in form.base_fields.keys():
            config = obj.get_registry_item_class().get_config()
            config_field = form.base_fields['config']
            config_field.widget.add_config_widgets(config)
        return form

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        broken_item = is_broken(obj)
        context.update({
            'is_broken': broken_item,
        })
        return super(RegisteredItemAdmin, self).render_change_form(request, context, add, change, form_url, obj)


def register(site):
    site.register(RegisteredItem, RegisteredItemAdmin)
