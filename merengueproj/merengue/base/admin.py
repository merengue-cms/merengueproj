import datetime

from django import forms
from django import template
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.related import RelatedObject
from django.db.models.fields.related import ForeignKey
from django.shortcuts import render_to_response
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminOriginal
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.util import unquote, flatten_fieldsets
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.sites.admin import Site, SiteAdmin
from django.forms.models import ModelForm, BaseInlineFormSet, \
                                fields_for_model, save_instance, modelformset_factory
from django.forms.util import ValidationError
from django.forms.widgets import Media
from django.http import HttpResponseRedirect, Http404
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.importlib import import_module
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from cmsutils.forms.widgets import AJAXAutocompletionWidget
from transmeta import (canonical_fieldname, get_all_translatable_fields,
                       get_real_fieldname_in_each_language,
                       get_fallback_fieldname)

from merengue.base.adminsite import site
from merengue.base.forms import AdminBaseContentOwnersForm
from merengue.base.models import BaseContent, ContactInfo
from merengue.base.widgets import (CustomTinyMCE, ReadOnlyWidget,
                                   RelatedBaseContentWidget)
from genericforeignkey.admin import GenericAdmin

# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False


def register_app(app_name, admin_site=None):
    admin_function(function_name='register', app_name=app_name,
                   admin_site=admin_site)


def unregister_app(app_name, admin_site=None):
    admin_function(function_name='unregister', app_name=app_name,
                   admin_site=admin_site)


def admin_function(function_name, app_name, admin_site=None):
    import imp

    if admin_site is None:
        admin_site = site

    # we ensure we not registered twice or unregister unexisting
    if function_name == 'register' and app_name in admin_site.apps_registered:
        return
    elif function_name == 'unregister' and app_name not in admin_site.apps_registered:
        return

    # For each app, we need to look for an admin.py inside that app's
    # package. We can't use os.path here -- recall that modules may be
    # imported different ways (think zip files) -- so we need to get
    # the app's __path__ and look for admin.py on that path.

    # Step 1: find out the app's __path__ Import errors here will (and
    # should) bubble up, but a missing __path__ (which is legal, but weird)
    # fails silently -- apps that do weird things with __path__ might
    # need to roll their own admin registration.
    try:
        app_path = import_module(app_name).__path__
    except AttributeError:
        return

    # Step 2: use imp.find_module to find the app's admin.py. For some
    # reason imp.find_module raises ImportError if the app can't be found
    # but doesn't actually try to import the module. So skip this app if
    # its admin.py doesn't exist
    try:
        imp.find_module('admin', app_path)
    except ImportError:
        return

    # Step 3: import the app's admin file. If this has errors we want them
    # to bubble up.
    mod = __import__('%s.admin' % app_name, {}, {}, app_name.split('.'))

    # Step 4: look for register function and call it, passing admin site
    # as parameter
    register_func = getattr(mod, function_name, None)
    if register_func is not None and callable(register_func):
        register_func(admin_site)

    # finally, we add/remove this app to admin site registry
    if function_name == 'register':
        admin_site.apps_registered.append(app_name)
    else:
        admin_site.apps_registered.remove(app_name)


def autodiscover(admin_site=None):
    """
    Like Django autodiscover, it search for admin.py modules and fail silently
    when not present.

    Main difference is that you can pass admin_site by parameter for
    registration in this admin site.
    """
    # Bail out if autodiscover didn't finish loading from a previous call so
    # that we avoid running autodiscover again when the URLconf is loaded by
    # the exception handler to resolve the handler500 view.  This prevents an
    # admin.py module with errors from re-registering models and raising a
    # spurious AlreadyRegistered exception (see #8245).
    global LOADING
    if LOADING:
        return
    LOADING = True

    if admin_site is None:
        admin_site = site

    for app in settings.INSTALLED_APPS:
        register_app(app, admin_site)

    # autodiscover was successful, reset loading flag.
    LOADING = False


# Merengue Model Admins -----


class UserCreationFormCust(UserCreationForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'[^/]+$',
        error_message = _("This value must contain only letters, @, numbers and underscores."))


class UserChangeFormCust(UserChangeForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'[^/]+$',
        error_message = _("This value must contain only letters, @, numbers and underscores."))


class ReverseAdminInline(admin.StackedInline):

    class ReverseAdminFormSet(BaseInlineFormSet):

        def __init__(self, data=None, files=None, instance=None,
                     save_as_new=False, prefix=None):
            prefix = prefix or self.fk_field_name
            if instance is None:
                self.instance = self.model()
            else:
                self.instance = instance
            self.save_as_new = save_as_new
            field = getattr(self.instance, self.fk_field_name, None)
            if field:
                qs = self.model._default_manager.filter(id=field.id)
            else:
                qs = self.model._default_manager.get_empty_query_set()
            super(BaseInlineFormSet, self).__init__(data, files, prefix=prefix, queryset=qs)

        def add_fields(self, form, index):
            # we don't want BaseInlineFormSet add_fields cause it search the field
            # defined as a foreign key in the inline model
            return super(BaseInlineFormSet, self).add_fields(form, index)

        def save_new(self, form, commit=True):
            """Saves and returns a new model instance for the given form."""
            attr_instance = save_instance(form, self.model(), commit=commit)
            if attr_instance.id and self.instance and commit:
                setattr(self.instance, self.fk_field_name, attr_instance)
                self.instance.save()
            return attr_instance

        def save(self, commit=True):
            attr_instance = BaseInlineFormSet.save(self, commit)
            # If we change the related object then save the parent object in order
            # to fire posible events
            if commit:
                self.instance.save()
            return attr_instance

        @classmethod
        def get_default_prefix(cls):
            # we make fix the prefix to "form" to avoid problems with Django >= r10019
            # (not the production one). See ticket #1616
            return 'form'
    formset = ReverseAdminFormSet

    def _inlineformset_factory(self, parent_model, model, form=ModelForm,
                               formset=ReverseAdminFormSet, fk_name=None,
                               fields=None, exclude=None,
                               extra=3, can_order=False, can_delete=True, max_num=0,
                               formfield_callback=lambda f: f.formfield()):
        max_num = 1
        if fields is not None:
            fields = list(fields)
        else:
            # get all the fields for this model that will be generated.
            fields = fields_for_model(model, fields, exclude, formfield_callback).keys()
        kwargs = {
            'form': form,
            'formfield_callback': formfield_callback,
            'formset': formset,
            'extra': extra,
            'can_delete': can_delete,
            'can_order': can_order,
            'fields': fields,
            'exclude': exclude,
            'max_num': max_num,
        }
        FormSet = modelformset_factory(model, **kwargs)
        FormSet.fk_field_name = self.parent_fk_name
        #FormSet.fk = fk
        return FormSet

    def get_formset(self, request, obj=None, **kwargs):
        """Returns a BaseInlineFormSet class for use in admin add/change views."""
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        defaults = {
            "form": self.form,
            "formset": self.formset,
            "fk_name": self.fk_name,
            "fields": fields,
            "exclude": exclude + kwargs.get("exclude", []),
            "formfield_callback": self.formfield_for_dbfield,
            "extra": self.extra,
            "max_num": self.max_num,
            "can_delete": False,
        }
        defaults.update(kwargs)
        return self._inlineformset_factory(self.parent_model, self.model, **defaults)


def set_field_read_only(field, field_name, obj):
    """ utility function for convert a widget field into a read only widget """
    if hasattr(obj, 'get_%s_display' % field_name):
        display_value = getattr(obj, 'get_%s_display' % field_name)()
    else:
        display_value = None
    field.widget = ReadOnlyWidget(getattr(obj, field_name, ''), display_value)
    field.required = False


class BaseAdmin(GenericAdmin, admin.ModelAdmin):
    html_fields = ()
    autocomplete_fields = {}
    edit_related = ()
    readonly_fields = ()
    removed_fields = ()
    list_per_page = 50
    inherit_actions = True

    def __init__(self, model, admin_site):
        super(BaseAdmin, self).__init__(model, admin_site)
        # add all translatable fields to search_fields parameter
        # i.e. if search_fields = ('name',) would change to ('name_es', 'name_en',)
        trans_fields = get_all_translatable_fields(self.model)
        trans_search_fields = []
        for f in self.search_fields:
            if f in trans_fields:
                for trans_f in get_real_fieldname_in_each_language(f):
                    trans_search_fields.append(trans_f)
            else:
                trans_search_fields.append(f)
        self.search_fields = tuple(trans_search_fields)

    def _get_base_content(self, request, object_id=None, model_admin=None):
        if not object_id:
            object_id = self.admin_site.base_object_ids.get(self.tool_name, None)
        if not model_admin:
            model_admin = self.admin_site.base_tools_model_admins.get(self.tool_name, None)
        model = model_admin.model
        opts = model._meta

        try:
            obj = model.objects.get(pk=unquote(object_id))
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None

        if not model_admin.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        self.basecontent = obj
        return obj

    def get_form(self, request, obj=None):
        form = super(BaseAdmin, self).get_form(request, obj)
        if hasattr(self, 'readonly_fields'):
            for field_name in self.readonly_fields:
                if field_name in form.base_fields:
                    field = form.base_fields[field_name]
                    set_field_read_only(field, field_name, obj)
        return form

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(BaseAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        db_fieldname = canonical_fieldname(db_field)

        # tinymce editor for html fields
        if db_fieldname in self.html_fields:
            field.widget = CustomTinyMCE()
        elif db_field.name in self.autocomplete_fields:
            options = self.autocomplete_fields[db_field.name].copy()
            if 'choices' in options:
                choices = options.pop('choices')
                field.widget = AJAXAutocompletionWidget(choices=choices, attrs=options)
            elif 'url' in options: # Must have url or choices defined
                url = options.pop('url')
                field.widget = AJAXAutocompletionWidget(url=url, attrs=options)
        elif db_fieldname in self.removed_fields:
            return

        if db_fieldname == 'name' and field and field.required:
            old_clean = field.clean

            def new_clean(value):
                if isinstance(value, basestring) and not value.strip():
                    raise ValidationError(_(u'This field is required.'))
                return old_clean(value)
            field.clean = new_clean

        if field and isinstance(db_field, ForeignKey):
            if db_field.related.parent_model == BaseContent:
                field.widget = RelatedBaseContentWidget(field.widget, field.widget.rel, field.widget.admin_site)
        return field

    def get_actions(self, request):
        """ by default, this admin does not return all hierarchy actions of all parents model admins """
        if self.inherit_actions:
            return super(BaseAdmin, self).get_actions(request)
        else:
            return self.get_not_inherited_actions(request)

    def get_not_inherited_actions(self, request):
        """ by default, this admin does not return all hierarchy actions of all parents model admins """
        class_actions = getattr(self.__class__, 'actions', [])
        actions = []
        actions.extend([self.get_action(action) for action in class_actions])

        actions.sort(lambda a, b: cmp(a[2].lower(), b[2].lower()))
        actions = SortedDict([
            (name, (func, name, desc))
            for func, name, desc in actions])

        return actions

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """ overrided for allow editing related objects in admin with "edit_related" option """
        # XXX: it's a little harcoded, and can be improved
        if change and self.edit_related:
            object = context['original']
            edit_related_fields = []
            for related_field in self.edit_related:
                # we add only for editing all the edit_related fields
                related_manager = getattr(object, related_field)
                related_model = related_manager.model
                field_label = capfirst(force_unicode(related_model._meta.verbose_name_plural))
                all_related = related_model._default_manager.all()
                selected_objects_ids = [o.id for o in related_manager.all()]
                related_objects = []
                for obj in all_related:
                    related_obj_dict = {'object': obj, 'selected': False}
                    if obj.id in selected_objects_ids:
                        related_obj_dict['selected'] = True
                    related_objects.append(related_obj_dict)

                related_field_dict = {
                                'field_name': related_field,
                                'field_label': field_label,
                                'related_objects': related_objects,
                }
                edit_related_fields.append(related_field_dict)
            media = Media()
            media.add_js([settings.ADMIN_MEDIA_PREFIX + "js/SelectBox.js",
                          settings.ADMIN_MEDIA_PREFIX + "js/SelectFilter2.js", ])
            context.update({
                'edit_related_fields': edit_related_fields,
                'media': context['media'] + media.render(),
            })
        return super(BaseAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        """
        Hack for saving related object from edit_related admin option
        """
        super(BaseAdmin, self).save_model(request, obj, form, change)
        if change and self.edit_related:
            for related_field in self.edit_related:
                related_manager = getattr(obj, related_field)
                related_model = related_manager.model
                selected_ids = [int(data) for data in request.POST.getlist('edit_related_%s' % related_field)]
                related_ids = [o.id for o in related_manager.all()]
                # deleting related objects not selected by user
                for id_obj in related_ids:
                    if id_obj not in selected_ids:
                        object_to_remove = related_model._default_manager.get(id=id_obj)
                        related_manager.remove(object_to_remove)
                # adding selected objects not already related to object
                for id_obj in selected_ids:
                    if id_obj not in related_ids:
                        object_to_add = related_model._default_manager.get(id=id_obj)
                        related_manager.add(object_to_add)

    def confirm_action(self, request, queryset=None, extra_context=None,
                       confirm_template="admin/confirm_action.html"):
        """A generic confirm view for admin actions, taken from
        django-batchadmin"""

        if not queryset:
            queryset = self.model._default_manager.none()

        opts = self.model._meta
        app_label = opts.app_label
        selected_objects = []
        context = {}
        checkbox = u'''<input class="batch-select" type="checkbox" name="%(name)s"
                    value="%(object_id)s" checked="true"/>%(model_name)s: %(object_name)s'''
        checkbox_data = {'name': admin.ACTION_CHECKBOX_NAME,
                         'model_name': escape(force_unicode(capfirst(opts.verbose_name))),
                        }
        for i, obj in enumerate(queryset):
            if not self.has_change_permission(request, obj):
                raise PermissionDenied
            checkbox_data['object_name'] = escape(obj)
            checkbox_data['object_id'] = obj.id
            selected_objects.append([mark_safe(checkbox % checkbox_data), []])
            perms_needed = set()
            context = {
                "title": _("Are you sure?"),
                "object_name": force_unicode(opts.verbose_name),
                "object": obj,
                "selected_objects": selected_objects,
                "perms_lacking": perms_needed,
                "opts": opts,
                "root_path": self.admin_site.root_path,
                "app_label": app_label,
                "objects_id": queryset,
            }
            context.update(extra_context or {})

        return render_to_response(confirm_template,
                                  context,
                                  context_instance=template.RequestContext(request))

    def _base_update_extra_context(self, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({'model_admin': self})
        return extra_context

    def changelist_view(self, request, extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        return super(BaseAdmin, self).changelist_view(request, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        return super(BaseAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        return super(BaseAdmin, self).change_view(request, object_id, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        return super(BaseAdmin, self).history_view(request, object_id, extra_context)


class BaseCategoryAdmin(BaseAdmin):
    ordering = (get_fallback_fieldname('name'), )
    search_fields = (get_fallback_fieldname('name'), )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}


class WorkflowBatchActionProvider(object):

    def set_as_draft(self, request, queryset):
        return self.change_state(request, queryset, 'draft',
                                 ugettext(u'Are you sure you want to set this items as draft?'),
                                 'base.can_draft')
    set_as_draft.short_description = _("Set as draft")

    def set_as_pending(self, request, queryset):
        return self.change_state(request, queryset, 'pending',
                                 ugettext(u'Are you sure you want to set this items as pending?'),
                                 'base.can_pending')
    set_as_pending.short_description = _("Set as pending")

    def set_as_published(self, request, queryset):
        return self.change_state(request, queryset, 'published',
                                 ugettext(u'Are you sure you want to set this items as published?'),
                                 'base.can_publish')
    set_as_published.short_description = _("Set as published")

    def change_state(self, request, queryset, state, confirm_msg, perm=None):
        if (perm and not request.user.has_perm(perm)) or not self.has_change_permission(request):
            raise PermissionDenied
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            if request.POST.get('post', False):
                updated = queryset.update(status=state)
                obj_log = ugettext("Changed to %s") % state
                msg_data = {'number': updated,
                            'model_name': self.opts.verbose_name,
                            'state': state}
                msg = ugettext(u"Successfully set %(number)d %(model_name)s as %(state)s.") % msg_data
                for obj in queryset:
                    self.log_change(request, obj, obj_log)
                    obj.save()
                self.message_user(request, msg)
            else:
                extra_context = {'title': confirm_msg,
                                 'action_submit': 'set_as_%s' % state}
                return self.confirm_action(request, queryset, extra_context)
    change_state.short_description = _(u"Change state of selected %(verbose_name_plural)s")


class StatusControlProvider(object):

    def _get_status_options(self, user, obj):
        options = set()
        all_options = set(settings.STATUS_LIST)

        if hasattr(obj, 'owners'):
            if not obj or user in obj.owners.all():
                options=options.union([o for o in all_options if o[0] in ('draft', 'pending')])
        # Remember that superuser has all the perms
        if user.has_perm('base.can_draft'):
            options=options.union([o for o in all_options if o[0] == 'draft'])
        if user.has_perm('base.can_pending'):
            options=options.union([o for o in all_options if o[0] == 'pending'])
        if user.has_perm('base.can_published'):
            options=options.union([o for o in all_options if o[0] == 'published'])
        return options


class BaseContentAdmin(BaseAdmin, WorkflowBatchActionProvider, StatusControlProvider):
    change_list_template = "admin/basecontent/change_list.html"
    list_display = ('name', 'status', 'user_modification_date', 'last_editor')
    search_fields = ('name', )
    date_hierarchy = 'creation_date'
    list_filter = ('status', 'user_modification_date', 'last_editor', )
    select_list_filter = ('class_name', 'status', 'user_modification_date', )
    actions = ['set_as_draft', 'set_as_pending', 'set_as_published', 'assign_owners']
    filter_horizontal = ('owners', )
    edit_related = ()
    html_fields = ('description', )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}
    autocomplete_fields = {'tags': {'url': '/ajax/autocomplete/tags/base/basecontent/',
                                    'multiple': True,
                                    'multipleSeparator': " ",
                                    'size': 100}, }

    def add_owners(self, request, queryset, owners):
        if self.has_change_permission(request):
            selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
            n = queryset.count()
            obj_log = ugettext("Assigned owners")
            msg = "Successfully set owners for %d %s." % (n, self.opts.verbose_name)
            if n:
                owner_list = User.objects.filter(id__in=owners)
                for obj in queryset:
                    for owner in owner_list:
                        obj.owners.add(owner)
                    self.log_change(request, obj, obj_log)
                self.message_user(request, msg)

    def assign_owners(self, request, queryset):
        if not request.user.is_superuser:
            raise PermissionDenied
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            if request.POST.get('post', False):
                owners = request.POST.getlist('owners')
                return self.add_owners(request, queryset, owners)
            form = AdminBaseContentOwnersForm()
            extra_context = {'title': _('Are you sure you want to assign these owners to these contents?'),
                             'action_submit': 'assign_owners',
                             'form': form,
                            }
            return self.confirm_action(request, queryset, extra_context,
                                       confirm_template='admin/basecontent/assign_owners.html')
    assign_owners.short_description = _("Assign owners")

    def has_change_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        has_change_perm = super(BaseContentAdmin, self).has_change_permission(request, obj)
        if has_change_perm:
            return True
        if obj == None:
            return self.has_add_permission(request)
        elif hasattr(obj, 'can_edit'):
            return obj.can_edit(request.user)
        else:
            return hasattr(obj, 'owners') and request.user in obj.owners.all()

    def has_change_permission_to_any(self, request):
        return super(BaseContentAdmin, self).has_change_permission(request, None)

    def owner_is_needed(self, request):
        return not self.has_change_permission_to_any(request)

    def queryset(self, request):
        """
        Overrides Django admin queryset to add ownership based access control
        """
        qs = super(BaseContentAdmin, self).queryset(request)
        if self.owner_is_needed(request):
            # cannot edit all contents, only yours
            qs = qs.filter(owners=request.user)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        """
        Overrides Django admin behaviour
        """
        if not request.user.is_superuser:
            # we remove ownership selection
            kwargs.update({
                'exclude': ['owners'] + list(self.exclude) + kwargs.get("exclude", []),
            })
        form = super(BaseContentAdmin, self).get_form(request, obj, **kwargs)
        keys = form.base_fields.keys()
        if 'status' in keys:
            user = request.user
            options = self._get_status_options(user, obj)
            if options:
                form.base_fields['status'].choices = options
                if 'pending' in [o[0] for o in options]:
                    form.base_fields['status'].initial = 'pending'
            else:
                form.base_fields.pop('status')
        if 'main_image' in keys and\
           not request.user.has_perm('base.can_change_main_image'):
            form.base_fields.pop('main_image')
        if 'map_icon' in keys and\
           not request.user.has_perm('base.can_change_map_icon'):
            form.base_fields.pop('map_icon')

        return form

    def save_model(self, request, obj, form, change):
        """
        Hack for saving object as pending when user is editor
        """
        obj.last_editor = request.user

        # simulate auto_now=True for user_modification_date
        obj.user_modification_date = datetime.datetime.today()

        super(BaseContentAdmin, self).save_model(request, obj, form, change)

        if self.owner_is_needed(request):
            # user automatically get owner of this object
            obj.owners.add(request.user)

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(BaseContentAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        db_fieldname = canonical_fieldname(db_field)
        if db_fieldname == 'description':
            field.widget.attrs['rows'] = 4
        return field

    def changelist_view(self, request, extra_context=None):
        if request.GET.get('for_select', None):
            get = request.GET.copy()
            del(get['for_select'])
            request.GET = get
            return self.select_changelist_view(request, extra_context)
        return super(BaseContentAdmin, self).changelist_view(request, extra_context)

    def select_changelist_view(self, request, extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        opts = self.model._meta
        app_label = opts.app_label

        list_display = list(self.list_display)
        try:
            list_display.remove('action_checkbox')
        except ValueError:
            pass

        try:
            cl = ChangeList(request, self.model, list_display, self.list_display_links, self.select_list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_editable, self)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')
        cl.formset=None
        cl.params.update({'for_select': 1})
        context = {
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'media': self.media,
            'has_add_permission': False,
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
            'action_form': None,
            'actions_on_top': [],
            'actions_on_bottom': [],
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.change_list_template or [
            'admin/%s/%s/change_list.html' % (app_label, opts.object_name.lower()),
            'admin/%s/change_list.html' % app_label,
            'admin/change_list.html',
        ], context, context_instance=context_instance)

if settings.USE_GIS:
    BaseContentAdmin.list_display += ('google_minimap', )


class BaseContentViewAdmin(BaseContentAdmin):
    """ An special admin to find and edit all site contents """

    def has_add_permission(self, request):
        return False


class RelatedModelAdmin(BaseAdmin):
    """
    A related model admin. This admin will be appears

    Example use::

      class Book(models.Model):
          ...

      class Page(models.Model):
          book = models.ForeignKey(Book)
          ...

      class PageRelatedAdmin(RelatedModelAdmin):
          model = Page
          tool_name = 'pages'
          tool_label = 'book pages'
          related_field = 'book'

      >>> site.register_related(Page, PageRelatedAdmin, related_to=Book)
    """
    tool_name = None
    related_field = None
    one_to_one = False

    def __init__(self, *args, **kwargs):
        super(RelatedModelAdmin, self).__init__(*args, **kwargs)
        if not self.tool_name:
            pass
        if not self.related_field:
            pass
        for inline in self.inline_instances:
            inline.admin_model = self # for allow retrieving basecontent object

    def _update_extra_context(self, request, extra_context=None):
        extra_context = extra_context or {}
        basecontent = self._get_base_content(request)
        basecontent_type_id = ContentType.objects.get_for_model(basecontent).id
        extra_context.update({'related_admin_site': self.admin_site,
                              'basecontent': basecontent,
                              'basecontent_opts': basecontent._meta,
                              'basecontent_type_id': basecontent_type_id,
                              'inside_basecontent': True,
                              'selected': self.tool_name})
        return extra_context

    def is_created_one_to_one_object(self):
        obj = self.model._default_manager.filter(**{self.related_field: self.basecontent})
        if obj:
            return obj[0]
        return None

    def changelist_view(self, request, extra_context=None):
        extra_context = self._update_extra_context(request, extra_context)
        if self.one_to_one:
            obj_created = self.is_created_one_to_one_object()
            if obj_created:
                return HttpResponseRedirect('%s%s' % (request.get_full_path(), obj_created.pk))
            return HttpResponseRedirect('%sadd' % request.get_full_path())
        return super(RelatedModelAdmin, self).changelist_view(request, extra_context)

    def queryset(self, request, basecontent=None):
        base_qs = super(RelatedModelAdmin, self).queryset(request)
        if basecontent is None:
            # we override our related content
            basecontent = self.basecontent
        return base_qs.filter(**{self.related_field: basecontent})

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self._update_extra_context(request, extra_context)
        if self.one_to_one:
            obj_created = self.is_created_one_to_one_object()
            if obj_created:
                return HttpResponseRedirect('%s../%s' % (request.get_full_path(), obj_created.pk))
        return super(RelatedModelAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = self._update_extra_context(request, extra_context)
        return super(RelatedModelAdmin, self).change_view(request, object_id, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        extra_context = self._update_extra_context(request, extra_context)
        return super(RelatedModelAdmin, self).delete_view(request, object_id, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        extra_context = self._update_extra_context(request, extra_context)
        return super(RelatedModelAdmin, self).history_view(request, object_id, extra_context)

    def save_form(self, request, form, change):
        # we associate related object
        form.cleaned_data[self.related_field] = self.basecontent
        return super(BaseAdmin, self).save_form(request, form, change)

    def save_model(self, request, obj, form, change):
        super(RelatedModelAdmin, self).save_model(request, obj, form, change)
        opts = obj._meta
        field = opts.get_field_by_name(self.related_field)[0]
        if isinstance(field, RelatedObject) and \
           not isinstance(field.field, models.OneToOneField):
            # if related_field related foreign key (n elements)
            # we associate related object here
            manager = getattr(obj, field.get_accessor_name())
            through_model = getattr(manager, 'through', None)
            if through_model is None:
                # we only know how handle many 2 many without intermediate models
                manager.add(self.basecontent)
        self.custom_relate_content(request, obj, form, change)

    def custom_relate_content(self, request, obj, form, change):
        """
        Custom relation function. to override if child classes wants.
        Useful for example in many2many relations with intermediate models, because
        we don't know how to handle this.
        """
        pass

    def get_form(self, request, obj=None, **kwargs):
        form = super(RelatedModelAdmin, self).get_form(request, obj, **kwargs)
        self.remove_related_field_from_form(form)
        return form

    def remove_related_field_from_form(self, form):
        if self.related_field in form.base_fields.keys():
            form.base_fields.pop(self.related_field)


class BaseContentRelatedContactInfoAdmin(RelatedModelAdmin):
    tool_name = 'contact_info'
    tool_label = _('contact info')
    one_to_one = True
    related_field = 'basecontent'


class BaseOrderableInlines(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super(BaseOrderableInlines, self).__init__(*args, **kwargs)
        self.tabular_inline = False
        self.stacked_inline = False
        for inline in self.inlines:
            if inline.__base__ == admin.TabularInline:
                self.tabular_inline = True
            elif inline.__base__ == admin.StackedInline:
                self.stacked_inline = True

    def _media(self):
        __media = super(BaseOrderableInlines, self)._media()
        __media.add_js(['js/jquery-ui-1.8.dragdrop.min.js'])
        if self.stacked_inline:
            __media.add_js(['js/menu-sort-stacked.js'])
        if self.tabular_inline:
            __media.add_js(['js/menu-sort-tabular.js'])
        return __media
    media = property(_media)


class BaseOrderableAdmin(BaseAdmin):
    """
    A model admin that can reorder content by a sortablefield
    """
    change_list_template = "admin/basecontent/sortable_change_list.html"
    sortablefield = 'position'

    def changelist_view(self, request, extra_context=None):
        if request.method == 'POST':
            neworder = request.POST.get('neworder', None)
            page = request.GET.get('p', 0)
            if neworder is None:
                return super(BaseOrderableAdmin, self).changelist_view(request, extra_context)
            neworder = neworder.split(',')
            items = self.model.objects.filter(id__in=neworder)
            for item in items:
                newposition = neworder.index(unicode(item.id)) + (int(page) * 50)
                setattr(item, self.sortablefield, newposition)
                item.save()

        return super(BaseOrderableAdmin, self).changelist_view(request, extra_context)


class OrderableRelatedModelAdmin(RelatedModelAdmin):
    """
    A model admin that can reorder related content.

    Example use::

      class Book(models.Model):
          ...

      class Page(models.Model):
          books = models.ManyToManyField(Book, through='PageBook')

      class PageBook(models.Model):
          book = models.ForeignKey(Book)
          page = models.ForeignKey(Page)
          order = models.PositiveIntegerField()

      class PageOrderableRelatedAdmin(OrderableRelatedModelAdmin):
          model = Page
          tool_name = 'pages'
          tool_label = 'book pages'
          related_field = 'books'
          sortablefield = 'order'

          def get_relation_obj(self, through_model, obj):
              return through_model.objects.get(book=self.basecontent, page=obj)

      >>> site.register_related(Page, PageOrderableRelatedAdmin, related_to=Book)
    """
    change_list_template = "admin/basecontent/sortable_change_list.html"
    sortablefield = 'position'

    def get_ordering(self):
        """
        Returns ordering by sortablefield
        """
        opts = self.model._meta
        field = opts.get_field_by_name(self.related_field)[0]
        relation_lookup = field.field.rel.through.lower()
        return ('%s__order' % relation_lookup, 'asc')

    def changelist_view(self, request, extra_context=None):
        extra_context = self._update_extra_context(request, extra_context)
        if request.method == 'POST':
            neworder_list = request.POST.get('neworder', None)
            page = request.GET.get('p', 0)
            if neworder_list is None:
                return super(OrderableRelatedModelAdmin, self).changelist_view(request, extra_context)
            neworder_list = neworder_list.split(',')
            items = self.queryset(request).filter(id__in=neworder_list)
            for item in items:
                field = item._meta.get_field_by_name(self.related_field)[0]
                through_model = field.field.rel.through_model
                neworder = neworder_list.index(unicode(item.id)) + (int(page) * 50)
                relation = self.get_relation_obj(through_model, item)
                setattr(relation, self.sortablefield, neworder)
                relation.save()

        return super(OrderableRelatedModelAdmin, self).changelist_view(request, extra_context)

    def get_relation_obj(self, through_model, obj):
        """
        Callback method that get relationship content for a item.
        To override in subclasses. See example implementation above.
        """
        raise NotImplementedError('You have to override this method')


class UserAdmin(BaseAdmin, UserAdminOriginal):
    form = UserChangeFormCust
    add_form = UserCreationFormCust
    list_display = UserAdminOriginal.list_display + ('is_active', )
    list_filter = UserAdminOriginal.list_filter + ('is_active', )

    def __init__(self, model, admin_site):
        super(UserAdmin, self).__init__(model, admin_site)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        return super(BaseAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_context=None):
        return super(UserAdmin, self).change_view(request, object_id,
                                                  extra_context={'is_user_change_view': True})


def register(site):
    ## register admin models
    site.register(User, UserAdmin)
    site.register(Group, GroupAdmin)
    site.register(BaseContent, BaseContentViewAdmin)
    site.register(Site, SiteAdmin)
    register_related_base(site, BaseContent)
    if settings.USE_GIS:
        register_related_gis(site, BaseContent)


def register_related_base(site, related_to):
    site.register_related(ContactInfo, BaseContentRelatedContactInfoAdmin, related_to=related_to)



# ----- begin monkey patching -----

# we change ChangeList.get_ordering for allowing define a dynamic ordering
# Django does not allow that. We have create a ticket for fix that
# For more details, see django ticket http://code.djangoproject.com/ticket/12875
legacy_get_ordering = ChangeList.get_ordering


def new_get_ordering(self):
    if hasattr(self.model_admin, 'get_ordering'):
        return self.model_admin.get_ordering()
    return legacy_get_ordering(self)

ChangeList.get_ordering = new_get_ordering


if settings.USE_GIS:
    from django.contrib.gis import admin as geoadmin
    from django.contrib.gis.db import models as geomodels
    from django.contrib.gis.maps.google import GoogleMap
    from merengue.places.models import Location
    from merengue.base.widgets import (OpenLayersWidgetLatitudeLongitude,
                                   OpenLayersInlineLatitudeLongitude)


    GMAP = GoogleMap(key=settings.GOOGLE_MAPS_API_KEY)

    class LocationModelAdminMixin(object):

        title_first_fieldset = None

        def set_fieldset(self):
            """Returns a BaseInlineFormSet class for use in admin add/change views."""
            render_message = ugettext('Click to Locate')
            adding = "<a name 'ajax_geolocation'>(<a href='#ajax_geolocation' class='ajax_geolocation'>%s</a>) <input id='id_input_ajax' type='text' class='input_ajax'><img id='img_ajax_loader' src='%simg/ajax-loader-transparent.gif' class='hide ajax_geolocation' />" % (render_message, settings.MEDIA_URL)

            title_fieldset = mark_safe("%s %s" % (ugettext(u'Location Maps'), adding))

            self.fieldsets = (
                (self.title_first_fieldset, {'fields': ('address', 'postal_code', )}),
                (title_fieldset,
                    {'fields': ('main_location', 'borders', )}
                ),
            )

        def get_form(self, request, obj=None):
            form = super(LocationModelAdminMixin, self).get_form(request, obj)
            self.set_fieldset()
            return form

        def get_formset(self, request, obj=None, **kwargs):
            form_set = super(LocationModelAdminMixin, self).get_formset(request, obj)
            self.set_fieldset()
            return form_set

        def formfield_for_dbfield(self, db_field, **kwargs):
            if isinstance(db_field, geomodels.GeometryField):
                request = kwargs.pop('request', None)
                # Setting the widget with the newly defined widget.
                kwargs['widget'] = self.get_map_widget(db_field)
                return db_field.formfield(**kwargs)
            else:
                return super(LocationModelAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)

        def _media(self):
            __media = super(LocationModelAdminMixin, self)._media()
            __media.add_js(['merengue/js/gis/osmgeoadmin.latitude.longitude.js'])
            return __media
        media = property(_media)

    class OSMGeoAdminLatitudeLongitude(geoadmin.OSMGeoAdmin):
        widget = OpenLayersWidgetLatitudeLongitude

    class InlineLocationModelAdmin(LocationModelAdminMixin):

        def __init__(self, parent_model, admin_site):
            from merengue.places.admin import GoogleAdmin

            super(InlineLocationModelAdmin, self).__init__(parent_model, admin_site)
            self.geoModelAdmin = GoogleAdmin(parent_model, admin_site)
            self.geoModelAdmin.widget = OpenLayersInlineLatitudeLongitude
            self.geoModelAdmin.map_template = 'admin/gis/google_inline.html'

        def _media(self, *args, **kwargs):
            media_super = super(InlineLocationModelAdmin, self)._media(*args, **kwargs)
            media_geo = self.geoModelAdmin._media(*args, **kwargs)
            media_super.add_js(media_geo._js)
            media_super.add_css(media_geo._css)
            media_super.add_js(['js/gis/osmgeoadmin.latitude.longitude.js'])
            return media_super
        media = property(_media)

        def get_formset(self, request, obj=None, **kwargs):
            """Returns a BaseInlineFormSet class for use in admin add/change views."""
            self.set_fieldset()
            return super(InlineLocationModelAdmin, self).get_formset(request, obj, **kwargs)

        def get_map_widget(self, *args, **kwargs):
            return self.geoModelAdmin.get_map_widget(*args, **kwargs)

    class BaseContentRelatedLocationModelAdmin(LocationModelAdminMixin, RelatedModelAdmin, OSMGeoAdminLatitudeLongitude):
        tool_name = 'location'
        tool_label = _('location')
        one_to_one = True
        related_field = 'basecontent'
        extra_js = [GMAP.api_url + GMAP.key]
        map_width = 500
        map_height = 300
        default_zoom = 10
        default_lat = 4500612.0
        default_lon = -655523.0
        map_template = 'admin/gis/google.html'
        title_first_fieldset = _('Address')

    def setup_basecontent_admin(basecontent_admin_site):
        basecontent_admin_site.register(Location, BaseContentRelatedLocationModelAdmin)

    def register_related_gis(site, related_to):
        site.register_related(Location, BaseContentRelatedLocationModelAdmin, related_to=related_to)
