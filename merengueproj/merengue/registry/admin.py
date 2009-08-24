from base.admin import BaseAdmin
from registry.models import RegisteredItem
from registry.widgets import ConfigWidget


class RegisteredItemAdmin(BaseAdmin):
    readonly_fields = ('class_name', 'module', 'category', )
    list_display = ('class_name', 'module', 'category', )
    list_filter = ('category', )

    def get_form(self, request, obj=None, **kwargs):
        form = super(RegisteredItemAdmin, self).get_form(request, obj, **kwargs)

        if 'config' in form.base_fields.keys():
            config_field = form.base_fields['config']
            # HACK: django version error? :S
            if not isinstance(config_field.widget, ConfigWidget):
                config_field.widget = ConfigWidget()
            config_field.widget.add_config_widgets(obj.get_registry_item_class().get_config())
        return form


def register(site):
    site.register(RegisteredItem, RegisteredItemAdmin)
