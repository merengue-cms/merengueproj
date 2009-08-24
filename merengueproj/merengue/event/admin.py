from django import template
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.forms import DateField
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import BaseContentAdmin, BaseAdmin, BaseContentRelatedModelAdmin, Location, ReverseAdminInline
from merengue.base.admin import InlineLocationModelAdmin
from merengue.base.models import BaseContent, ContactInfo
from merengue.base.widgets import AdminDateOfDateTimeWidget
from batchadmin.forms import CHECKBOX_NAME
from batchadmin.util import get_changelist
from event.models import Event, Occurrence, Category, CategoryGroup

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


class EventRelatedOccurrenceAdmin(BaseContentRelatedModelAdmin):
    change_list_template = 'admin/event/occurrence/change_list.html'
    change_form_template = 'admin/event/occurrence/change_form.html'
    list_display = ('__str__', 'start', 'end', 'google_minimap')
    list_filter = ('start', 'end', )
    html_fields = ('price', 'schedule', )
    inlines = [OccurrenceContactInfoAdminInline, OccurrenceLocationAdminInline]

    def __init__(self, *args, **kwargs):
        super(EventRelatedOccurrenceAdmin, self).__init__(*args, **kwargs)
        self.basecontent_admin = BaseContentLocationOccurrenceAdmin(BaseContent, self.admin_site)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        opts = obj._meta
        pk_value = obj._get_pk_val()

        msg = ugettext('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}

        if "_content_locate" in request.POST.keys():
            self.message_user(request, msg + u' ' + ugettext('You can select a content to place your location.'))
            return HttpResponseRedirect(post_url_continue % pk_value + 'content_locate/')
        return super(EventRelatedOccurrenceAdmin, self).response_add(request, obj, post_url_continue)

    def queryset(self, request):
        return self.admin_site.basecontent.occurrence_event.all()

    def save_model(self, request, obj, form, change):
        obj.event = self.admin_site.basecontent
        super(EventRelatedOccurrenceAdmin, self).save_model(
                request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super(EventRelatedOccurrenceAdmin, self).get_form(
                request, obj, **kwargs)
        if 'event' in form.base_fields.keys():
            form.base_fields.pop('event')
        return form

    def get_formsets(self, request, obj=None):
        for inline in self.inline_instances:
            if isinstance(inline, OccurrenceLocationAdminInline) and\
               obj and obj.basecontent_location:
                continue
            yield inline.get_formset(request, obj)

    def save_formset(self, request, form, formset, change):
        """ override method for updating event location from all occurrences """
        formset.save()
        formset.instance.event.update_location()

    def __call__(self, request, url):
        if url and 'content_locate' in url:
            new_url = url[url.find('content_locate')+15:] or None
            object_id = url[:url.find('/content_locate')]
            try:
                if object_id == 'add':
                    self.basecontent_admin.occurrence=None
                else:
                    obj = self.model._default_manager.get(pk=unquote(object_id))
                    self.basecontent_admin.occurrence=obj
                return self.basecontent_admin(request, new_url)
            except self.model.DoesNotExist:
                pass
        elif url and url.endswith('content_unplace'):
            url = url[:url.find('/content_unplace')]
            return self.unplace(request, unquote(url))
        return super(EventRelatedOccurrenceAdmin, self).__call__(request, url)

    def unplace(self, request, object_id):
        opts = self.model._meta

        try:
            obj = self.model._default_manager.get(pk=unquote(object_id))
        except self.model.DoesNotExist:
            obj = None

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404('%s object with primary key %r does not exist.' % (force_unicode(opts.verbose_name), escape(object_id)))

        if request.method=='POST':
            old_location = obj.basecontent_location
            if old_location:
                obj.basecontent_location=None
                obj.save()
                msg = ugettext(u"Occurrence is no longer placed at content %s." % old_location)
                self.message_user(request, msg)
            return HttpResponseRedirect("../")
        else:
            return render_to_response('admin/event/occurrence/unplace.html',
                                      {'occurrence': obj},
                                      context_instance=template.RequestContext(request))

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(EventRelatedOccurrenceAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['start', 'end']:
            field = DateField(label=field.label)
            field.widget = AdminDateOfDateTimeWidget()
        return field

admin.site.register(Category, EventCategoryAdmin)
admin.site.register(CategoryGroup, EventCategoryGroupAdmin)
admin.site.register(Event, EventAdmin)


def setup_event_admin(event_admin):
    event_admin.register(Occurrence, EventRelatedOccurrenceAdmin)
