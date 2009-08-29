from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import RelatedModelAdmin, BaseContentAdmin, BaseAdmin, Location, ReverseAdminInline
from merengue.base.admin import InlineLocationModelAdmin
from merengue.base.models import ContactInfo
from batchadmin.forms import CHECKBOX_NAME
from batchadmin.util import get_changelist
from plugins.event.models import Event, Occurrence, Category, CategoryGroup

SECTIONS_SLUG_EXCLUDE = ('eventos', )


class EventCategoryAdmin(BaseAdmin):
    ordering = ('name_es', )
    search_fields = ('name_es', )

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(EventCategoryAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'sections':
            field.choices.queryset = field.choices.queryset.exclude(slug__in=SECTIONS_SLUG_EXCLUDE)
            field.widget.choices.queryset = field.widget.choices.queryset.exclude(slug__in=SECTIONS_SLUG_EXCLUDE)
        return field


class EventCategoryGroupAdmin(BaseAdmin):
    ordering = ('name_es', )
    search_fields = ('name_es', )

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(EventCategoryGroupAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'sections':
            field.choices.queryset = field.choices.queryset.exclude(slug__in=SECTIONS_SLUG_EXCLUDE)
            field.widget.choices.queryset = field.widget.choices.queryset.exclude(slug__in=SECTIONS_SLUG_EXCLUDE)
        return field


class EventAdmin(BaseContentAdmin):
    ordering = ('name_es', )
    search_fields = ('name', )
    exclude = ('expire_date', )
    list_display = ('name', 'google_minimap', 'cached_min_start', 'cached_max_end', 'status', 'user_modification_date', 'last_editor')
    list_filter = ('categories', 'frequency', 'status', 'user_modification_date', )
    change_list_template = ""

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventAdmin, self).get_form(request, obj, **kwargs)
        if 'name' in form.base_fields.keys():
            form.base_fields.pop('name')
        form.base_fields.keyOrder.sort(lambda x, y: x.startswith('title_') and -1 or 1)
        return form

    def response_add(self, request, obj, post_url_continue='../%s/'):
        opts = obj._meta
        pk_value = obj._get_pk_val()

        msg = ugettext('The %(name)s "%(obj)s" was added successfully.'
                       'You may edit its occurrences below.') % {'name': force_unicode(opts.verbose_name),
                                                                 'obj': force_unicode(obj)}
        if "_save" in request.POST.keys():
            a=obj.id
            occurrence = obj.occurrence_event.all()[0]
            self.message_user(request, msg)
            return HttpResponseRedirect('../%s/admin/event/occurrence/' % obj.id)
        else:
            return super(EventAdmin, self).response_add(request, obj)


class OccurrenceContactInfoAdminInline(ReverseAdminInline):
    model = ContactInfo
    verbose_name_plural = _('Ocurrence Contact Info')
    parent_fk_name = 'contact_info'


class OccurrenceLocationAdminInline(InlineLocationModelAdmin, ReverseAdminInline):
    model = Location
    verbose_name_plural = _('Ocurrence Locations')
    parent_fk_name = 'location'


class BaseContentLocationOccurrenceAdmin(BaseContentAdmin):
    list_display = ('name', 'google_minimap', 'status', 'class_name')

    list_filter = BaseContentAdmin.list_filter + ('class_name', )
    search_fields = ('name', )
    batch_actions = ['place_at', ]
    change_list_template = 'admin/event/occurrence/basecontent_location_change_list.html'

    def __init__(self, *args, **kwargs):
        super(BaseContentLocationOccurrenceAdmin, self).__init__(*args, **kwargs)
        if 'batchadmin_checkbox' in self.list_display:
            self.list_display.remove('batchadmin_checkbox')

    def queryset(self, request):
        # Do not return BaseContentAdmin.queryset
        return super(BaseContentAdmin, self).queryset(request)

    def has_change_permission(self, request, obj=None):
        opts = self.occurrence._meta
        return request.user.has_perm(opts.app_label + '.' + opts.get_add_permission())

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, extra_context=None):
        choices = self.batchadmin_choices
        if request.method == 'POST':
            changelist = get_changelist(request, self.model, self)
            action_index = int(request.POST.get('index', 0))
            data = {}
            for key in request.POST:
                if key not in (CHECKBOX_NAME, 'index'):
                    data[key] = request.POST.getlist(key)[action_index]
            action_form = self.batch_action_form(data, auto_id=None)
            action_form.fields['action'].choices = choices

            if action_form.is_valid():
                action = action_form.cleaned_data['action']
                response = self.batchadmin_dispatch(request, changelist, action)
                if isinstance(response, HttpResponse):
                    return response
                return HttpResponseRedirect("..")
        else:
            object = get_object_or_404(self.model, id=object_id)
            extra_context = {'title': ugettext('Are you sure you want to place occurrence at the following content?'),
                             'action_submit': 'place_at'}
            return self.confirm_action(request, [object_id], extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': _(u'Select where do you want to place the occurrence')}
        return super(BaseContentLocationOccurrenceAdmin, self).changelist_view(request, extra_context)

    def place_at(self, request, changelist):
        selected = request.POST.getlist(CHECKBOX_NAME)
        objects = changelist.get_query_set().filter(pk__in=selected)
        if len(objects) == 1:
            obj = objects[0]
            self.occurrence.basecontent_location = obj
            self.occurrence.save()
            self.occurrence.event.update_location()
            msg = ugettext(u"Successfully set occurrence location.")
            self.message_user(request, msg)
            return HttpResponseRedirect('../../')
        else:
            msg = ugettext(u"Ocurrence location not changed.")
            self.message_user(request, msg)
    place_at.short_description = "Set occurrence location at content location"


class RelatedOcurrenceAdmin(RelatedModelAdmin):
    tool_name = 'occurrences'
    related_field = 'event'
    list_display = ('__str__', 'start', 'end', 'google_minimap')
    list_filter = ('start', 'end', )
    html_fields = ('price', 'schedule', )


def register(site):
    site.register(Category, EventCategoryAdmin)
    site.register(CategoryGroup, EventCategoryGroupAdmin)
    site.register(Event, EventAdmin)
    site.register_related(Occurrence, RelatedOcurrenceAdmin, related_to=Event)
