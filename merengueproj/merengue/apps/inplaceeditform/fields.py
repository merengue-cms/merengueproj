from django.conf import settings
from django.contrib.admin.widgets import AdminSplitDateTime, AdminDateWidget
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.importlib import import_module
from django.utils.translation import ugettext

from inplaceeditform.commons import has_transmeta, apply_filters


class BaseAdaptorField(object):

    def __init__(self, field_name, obj, request,
                 filters_to_show=None, filters_to_edit=None,
                 class_inplace=None, tag_name_cover=None,
                 loads_tags=None,
                 **options):
        self.model = obj.__class__
        self.field_name_render = field_name  # To transmeta
        self.field_name = field_name
        self.obj = obj
        self.request = request
        self.filters_to_show = filters_to_show or []
        self.filters_to_edit = filters_to_edit or []
        self.class_inplace = class_inplace or ''
        self.tag_name_cover = tag_name_cover or 'span'
        self.loads_tags = loads_tags or []
        self.initial = {}
        self._transmeta_processing()
        self.options = options

    @property
    def name(self):
        return ''

    @property
    def classes(self):
        return 'inplaceedit %sinplaceedit' % (self.name)

    def get_form_class(self):
        return modelform_factory(self.model)

    def get_form(self):
        return self.get_form_class()(instance=self.obj,
                                     initial=self.initial)

    def get_field(self):
        field = self.get_form()[self.field_name]
        field = self._adding_size(field)
        return field

    def get_value_editor(self, value):
        return self.get_field().field.clean(value)

    def render_value(self, field_name=None):
        field_name = field_name or self.field_name_render
        value = getattr(self.obj, field_name)
        return apply_filters(value, self.filters_to_show, self.loads_tags)

    def render_value_edit(self):
        value = self.render_value()
        if value:
            return value
        return self.empty_value()

    def empty_value(self):
        return ugettext('Dobleclick to edit')

    def render_field(self, template_name="inplaceeditform/render_field.html"):
        return render_to_string(template_name,
                                {'form': self.get_form(),
                                 'field': self.get_field(),
                                 'class_inplace': self.class_inplace})

    def render_media_field(self, template_name="inplaceeditform/render_media_field.html"):
        return render_to_string(template_name,
                                {'field': self.get_field(),
                                 'MEDIA_URL': settings.MEDIA_URL,
                                 'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX})

    def render_config(self, template_name="inplaceeditform/render_config.html"):
        content_type = ContentType.objects.get_for_model(self.model)
        return render_to_string(template_name,
                                {'field_name': self.field_name_render,
                                 'obj': self.obj,
                                 'content_type': content_type,
                                 'filters_to_show': simplejson.dumps(self.filters_to_show),
                                 'filters_to_edit': simplejson.dumps(self.filters_to_edit),
                                 'adaptor': self.name,
                                 'class_inplace': self.class_inplace,
                                 'loads_tags': ':'.join(self.loads_tags),
                                 })

    def can_edit(self):
        can_edit_adaptor_path = getattr(settings, 'ADAPTOR_INPLACEEDIT_EDIT', None)
        if can_edit_adaptor_path:
            path_module, class_adaptor = ('.'.join(can_edit_adaptor_path.split('.')[:-1]),
                                          can_edit_adaptor_path.split('.')[-1])
            return getattr(import_module(path_module), class_adaptor).can_edit(self)
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def save(self, value):
        setattr(self.obj, self.field_name, value)
        self.obj.save()

    def treatment_height(self, height):
        return height

    def treatment_width(self, width):
        return width

    def _adding_size(self, field):
        attrs = field.field.widget.attrs
        if not 'style' in attrs:
            style = ''
            for key, value in self.options.items():
                if key == 'height':
                    value = self.treatment_height(value)
                elif key == 'width':
                    value = self.treatment_width(value)
                style += "%s: %s; " % (key, value)
            attrs['style'] = style
        field.field.widget.attrs = attrs
        return field

    def _transmeta_processing(self):
        if has_transmeta:
            import transmeta
            translatable_fields = self._get_translatable_fields(self.model)
            if self.field_name in translatable_fields:
                self.field_name = transmeta.get_real_fieldname(self.field_name)
                self.transmeta = True
                if not self.render_value(self.field_name):
                    self.initial = {self.field_name: ugettext('Write a traslation')}
                return
        self.transmeta = False

    def _get_translatable_fields(self, cls):
        classes = cls.mro()
        translatable_fields = []
        [translatable_fields.extend(cl._meta.translatable_fields) for cl in classes \
                                    if getattr(cl, '_meta', None) and getattr(cl._meta, 'translatable_fields', None)]
        return translatable_fields


class AdaptorTextField(BaseAdaptorField):

    @property
    def name(self):
        return 'text'

    def treatment_width(self, width):
        if width:
            width = float(width.replace('px', ''))
            width = width + width / 4
            return '%spx' % width
        return width


class AdaptorTextAreaField(BaseAdaptorField):

    @property
    def name(self):
        return 'textarea'

    @property
    def classes(self):
        return "textareainplaceedit %s" % super(AdaptorTextAreaField, self).classes


class BaseDateField(BaseAdaptorField):

    def render_media_field(self):
        return render_to_string("inplaceeditform/adaptor_date/render_media_field.html",
                                {'field': self.get_field(),
                                 'MEDIA_URL': settings.MEDIA_URL,
                                 'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX})


class AdaptorDateField(BaseDateField):

    @property
    def name(self):
        return 'date'

    def get_field(self):
        field = super(AdaptorDateField, self).get_field()
        field.field.widget = AdminDateWidget()
        return field

    def render_value(self, field_name=None):
        val = super(AdaptorDateField, self).render_value(field_name)
        if not isinstance(val, str) and not isinstance(val, unicode):
            val = apply_filters(val, ["date:'%s'" % settings.DATE_FORMAT])
        return val


class AdaptorDateTimeField(BaseDateField):

    @property
    def name(self):
        return 'datetime'

    def render_field(self, template_name="inplaceeditform/adaptor_datetime/render_field.html"):
        return super(AdaptorDateTimeField, self).render_field(template_name)

    def render_media_field(self):
        return render_to_string("inplaceeditform/adaptor_datetime/render_media_field.html",
                                {'field': self.get_field(),
                                 'ADMIN_MEDIA_PREFIX': settings.ADMIN_MEDIA_PREFIX})

    def get_field(self):
        field = super(AdaptorDateTimeField, self).get_field()
        field.field.widget = AdminSplitDateTime()
        return field

    def render_value(self, field_name=None):
        val = super(AdaptorDateTimeField, self).render_value(field_name)
        if not isinstance(val, str) and not isinstance(val, unicode):
            val = apply_filters(val, ["date:'%s'" % settings.DATETIME_FORMAT])
        return val


class AdaptorChoicesField(BaseAdaptorField):

    @property
    def name(self):
        return 'choices'

    def treatment_height(self, height):
        return '30px'

    def treatment_width(self, width):
        return '100px'

    def render_value(self, field_name=None):
        field_name = field_name or self.field_name
        value = getattr(self.obj, field_name)
        return apply_filters(value, self.filters_to_show).title()


class AdaptorForeingKeyField(BaseAdaptorField):

    @property
    def name(self):
        return 'fk'

    def treatment_height(self, height):
        return '30px'

    def treatment_width(self, width):
        return '100px'

    def render_value(self, field_name=None):
        value = super(AdaptorForeingKeyField, self).render_value(field_name)
        value = getattr(value, '__unicode__', None) and value.__unicode__() or None
        return value

    def get_value_editor(self, value):
        value = super(AdaptorForeingKeyField, self).get_value_editor(value)
        return value and value.pk

    def save(self, value):
        setattr(self.obj, "%s_id" % self.field_name, value)
        self.obj.save()


class AdaptorManyToManyField(BaseAdaptorField):

    @property
    def name(self):
        return 'm2m'

    def treatment_height(self, height):
        return '100px'

    def treatment_width(self, width):
        return '100px'

    def get_value_editor(self, value):
        return [item.pk for item in super(AdaptorManyToManyField, self).get_value_editor(value)]

    def render_value(self, field_name=None):
        return super(AdaptorManyToManyField, self).render_value(field_name).all()


class AdaptorCommaSeparatedManyToManyField(AdaptorManyToManyField):

    @property
    def name(self):
        return 'm2mcomma'

    def render_value(self, field_name=None, template_name="inplaceeditform/adaptor_m2m/render_commaseparated_value.html"):
        queryset = super(AdaptorCommaSeparatedManyToManyField, self).render_value(field_name)
        return render_to_string(template_name, {'queryset': queryset})
