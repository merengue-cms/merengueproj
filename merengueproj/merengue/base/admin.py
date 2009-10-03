import datetime

from django import forms
from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import models
from django.db.models.related import RelatedObject
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin as UserAdminOriginal
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.util import quote, unquote, flatten_fieldsets, _nest_help
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.gis import admin as geoadmin
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.maps.google import GoogleMap
from django.forms.models import ModelForm, BaseInlineFormSet, \
                                fields_for_model, save_instance, modelformset_factory
from django.forms.util import ErrorList, ValidationError
from django.forms.widgets import Media
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.importlib import import_module
from django.utils.text import capfirst
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from cmsutils.forms.widgets import AJAXAutocompletionWidget

from batchadmin.util import model_ngettext, get_changelist

from merengue.base.adminsite import site
from merengue.base.forms import AdminBaseContentOwnersForm
from merengue.base.models import Base, BaseContent, ContactInfo
from merengue.base.utils import geolocate_object_base, copy_request
from merengue.base.widgets import (CustomTinyMCE, OpenLayersWidgetLatitudeLongitude,
                          OpenLayersInlineLatitudeLongitude, ReadOnlyWidget)
from merengue.multimedia.models import BaseMultimedia
from merengue.places.models import Location
from merengue.section.models import Document

# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False


GMAP = GoogleMap(key=settings.GOOGLE_MAPS_API_KEY)


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

    from django.conf import settings

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


class OSMGeoAdminLatitudeLongitude(geoadmin.OSMGeoAdmin):
    widget = OpenLayersWidgetLatitudeLongitude


def transmeta_aware_fieldname(db_field):
    """ all "description_en", "description_fr", etc. field names will return "description" """
    return getattr(db_field, 'original_fieldname', db_field.name) # original_fieldname is set by transmeta


def set_field_read_only(field, field_name, obj):
    """ utility function for convert a widget field into a read only widget """
    if hasattr(obj, 'get_%s_display' % field_name):
        display_value = getattr(obj, 'get_%s_display' % field_name)()
    else:
        display_value = None
    field.widget = ReadOnlyWidget(getattr(obj, field_name, ''), display_value)
    field.required = False


class BaseAdmin(admin.ModelAdmin):
    html_fields = ()
    autocomplete_fields = {}
    edit_related = ()
    readonly_fields = ()
    removed_fields = ()
    list_per_page = 50
    inherit_actions = True

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
        db_fieldname = transmeta_aware_fieldname(db_field)

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

    def get_deleted_objects(self, deleted_objects, perms_needed, user, obj, opts, current_depth, admin_site):
        "Helper function that recursively populates deleted_objects."
        nh = _nest_help # Bind to local variable for performance
        if current_depth > 16:
            return # Avoid recursing too deep.
        opts_seen = []
        for related in opts.get_all_related_objects():
            has_admin = related.model in admin_site._registry
            if related.opts in opts_seen:
                continue
            opts_seen.append(related.opts)
            rel_opts_name = related.get_accessor_name()
            field = related.field
            delete_cascade = getattr(field, 'delete_cascade', True)
            if not delete_cascade:
                continue
            if isinstance(related.field.rel, models.OneToOneRel):
                try:
                    sub_obj = getattr(obj, rel_opts_name)
                except ObjectDoesNotExist:
                    pass
                else:
                    if has_admin:
                        p = '%s.%s' % (related.opts.app_label, related.opts.get_delete_permission())
                        if not user.has_perm(p):
                            perms_needed.add(related.opts.verbose_name)
                            # We don't care about populating deleted_objects now.
                            continue
                    if not has_admin:
                        # Don't display link to edit, because it either has no
                        # admin or is edited inline.
                        nh(deleted_objects, current_depth,
                            [u'%s: %s' % (capfirst(related.opts.verbose_name), force_unicode(sub_obj)), []])
                    else:
                        # Display a link to the admin page.
                        nh(deleted_objects, current_depth, [mark_safe(u'%s: <a href="../../../../%s/%s/%s/">%s</a>' %
                            (escape(capfirst(related.opts.verbose_name)),
                            related.opts.app_label,
                            related.opts.object_name.lower(),
                            sub_obj._get_pk_val(),
                            escape(sub_obj))), []])
                    self.get_deleted_objects(deleted_objects, perms_needed, user, sub_obj, related.opts, current_depth+2, admin_site)
            else:
                has_related_objs = False
                for sub_obj in getattr(obj, rel_opts_name).all():
                    has_related_objs = True
                    if not has_admin:
                        # Don't display link to edit, because it either has no
                        # admin or is edited inline.
                        nh(deleted_objects, current_depth,
                            [u'%s: %s' % (capfirst(related.opts.verbose_name), force_unicode(sub_obj)), []])
                    else:
                        # Display a link to the admin page.
                        nh(deleted_objects, current_depth, [mark_safe(u'%s: <a href="../../../../%s/%s/%s/">%s</a>' %
                            (escape(capfirst(related.opts.verbose_name)),
                            related.opts.app_label,
                            related.opts.object_name.lower(),
                            sub_obj._get_pk_val(),
                            escape(sub_obj))), []])
                    self.get_deleted_objects(deleted_objects, perms_needed, user, sub_obj, related.opts, current_depth+2, admin_site)
                # If there were related objects, and the user doesn't have
                # permission to delete them, add the missing perm to perms_needed.
                if has_admin and has_related_objs:
                    p = '%s.%s' % (related.opts.app_label, related.opts.get_delete_permission())
                    if not user.has_perm(p):
                        perms_needed.add(related.opts.verbose_name)
        for related in opts.get_all_related_many_to_many_objects():
            has_admin = related.model in admin_site._registry
            if related.opts in opts_seen:
                continue
            opts_seen.append(related.opts)
            rel_opts_name = related.get_accessor_name()
            has_related_objs = False

            # related.get_accessor_name() could return None for symmetrical relationships
            if rel_opts_name:
                rel_objs = getattr(obj, rel_opts_name, None)
                # HACK: object can have a m2m relation (rel_objs) but it can be related to no other objects (rel_objs.all())
                if rel_objs and rel_objs.all():
                    has_related_objs = True

            if has_related_objs:
                for sub_obj in rel_objs.all():
                    if not has_admin:
                        # Don't display link to edit, because it either has no
                        # admin or is edited inline.
                        nh(deleted_objects, current_depth, [_('One or more %(fieldname)s in %(name)s: %(obj)s') % \
                            {'fieldname': force_unicode(related.field.verbose_name), 'name': force_unicode(related.opts.verbose_name), 'obj': escape(sub_obj)}, []])
                    else:
                        # Display a link to the admin page.
                        nh(deleted_objects, current_depth, [
                            mark_safe((_('One or more %(fieldname)s in %(name)s:') % {'fieldname': escape(force_unicode(related.field.verbose_name)), 'name': escape(force_unicode(related.opts.verbose_name))}) + \
                            (u' <a href="../../../../%s/%s/%s/">%s</a>' % \
                                (related.opts.app_label, related.opts.module_name, sub_obj._get_pk_val(), escape(sub_obj)))), []])
            # If there were related objects, and the user doesn't have
            # permission to change them, add the missing perm to perms_needed.
            if has_admin and has_related_objs:
                p = u'%s.%s' % (related.opts.app_label, related.opts.get_change_permission())
                if not user.has_perm(p):
                    assert False
                    perms_needed.add(related.opts.verbose_name)

    def delete_view(self, request, objects_id=[], extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        "The 'delete' admin view for this model."
        if not isinstance(objects_id, list) and not isinstance(objects_id, tuple):
            # workaround to handle simple object deletion
            return self.simple_delete_view(request, objects_id, extra_context)
        opts = self.model._meta
        app_label = opts.app_label
        deleted_objects = []
        context = {}
        for i, object_id in enumerate(objects_id):
            try:
                obj = self.model._default_manager.get(pk=object_id)
            except self.model.DoesNotExist:
                # Don't raise Http404 just yet, because we haven't checked
                # permissions yet. We don't want an unauthenticated user to be able
                # to determine whether a given object exists.
                obj = None

            if not self.has_delete_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                raise Http404('%s object with primary key %r does not exist.' % (force_unicode(opts.verbose_name), escape(object_id)))

            # Populate deleted_objects, a data structure of all related objects that
            # will also be deleted.
            deleted_objects.append([mark_safe(u'<input class="batch-select" type="checkbox" name="selected" value="%s" checked="true"/>%s: <a href="../../%s/">%s</a>' % (quote(object_id), escape(force_unicode(capfirst(opts.verbose_name))), quote(object_id), escape(obj))), []])
            perms_needed = set()
            self.get_deleted_objects(deleted_objects[i], perms_needed, request.user, obj, opts, 1, self.admin_site)

            context = {
                "title": _("Are you sure?"),
                "object_name": force_unicode(opts.verbose_name),
                "object": obj,
                "deleted_objects": deleted_objects,
                "perms_lacking": perms_needed,
                "opts": opts,
                "root_path": self.admin_site.root_path,
                "app_label": app_label,
                "objects_id": objects_id,
            }
            context.update(extra_context or {})

        return render_to_response(self.delete_confirmation_template or [
            "admin/%s/%s/delete_confirmation_various.html" % (app_label, opts.object_name.lower()),
            "admin/%s/delete_confirmation_various.html" % app_label,
            "admin/delete_confirmation_various.html"],
            context, context_instance=template.RequestContext(request))

    def simple_delete_view(self, request, object_id, extra_context=None):
        "The 'delete' admin view for this model."
        opts = self.model._meta
        app_label = opts.app_label

        try:
            obj = self.model._default_manager.get(pk=unquote(object_id))
        except self.model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None

        if not self.has_delete_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        deleted_objects = [mark_safe(u'%s: <a href="../../%s/">%s</a>' % (escape(force_unicode(capfirst(opts.verbose_name))), object_id, escape(obj))), []]
        perms_needed = set()
        self.get_deleted_objects(deleted_objects, perms_needed, request.user, obj, opts, 1, self.admin_site)

        if request.POST: # The user has already confirmed the deletion.
            if perms_needed:
                raise PermissionDenied
            obj_display = force_unicode(obj)
            obj.delete()

            self.log_deletion(request, obj, obj_display)
            self.message_user(request, _('The %(name)s "%(obj)s" was deleted successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj_display)})

            if not self.has_change_permission(request, None):
                return HttpResponseRedirect("../../../../")
            return HttpResponseRedirect("../../")

        context = {
            "title": _("Are you sure?"),
            "object_name": force_unicode(opts.verbose_name),
            "object": obj,
            "deleted_objects": deleted_objects,
            "perms_lacking": perms_needed,
            "opts": opts,
            "root_path": self.admin_site.root_path,
            "app_label": app_label,
        }
        context.update(extra_context or {})
        return render_to_response(self.delete_confirmation_template or [
            "admin/%s/%s/delete_confirmation.html" % (app_label, opts.object_name.lower()),
            "admin/%s/delete_confirmation.html" % app_label,
            "admin/delete_confirmation.html",
        ], context, context_instance=template.RequestContext(request))

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
    ordering = ('name_es', )
    search_fields = ('name_es', )


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
                            'model_name': model_ngettext(self.opts, updated),
                            'state': state}
                msg = ugettext(u"Successfully set %(number)d %(model_name)s as %(state)s.") % msg_data
                for obj in queryset:
                    self.log_change(request, obj, obj_log)
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
    list_display = ('name', 'google_minimap', 'status', 'user_modification_date', 'last_editor')
    search_fields = ('name', )
    date_hierarchy = 'creation_date'
    list_filter = ('is_autolocated', 'status', 'user_modification_date', 'last_editor', )
    actions = ['set_as_draft', 'set_as_pending', 'set_as_published', 'assign_owners']
    filter_horizontal = ('owners', )
    edit_related = ()
    html_fields = ('description', )
    prepopulated_fields = {'slug': ('name_es', )}
    exclude = ('main_image', )
    autocomplete_fields = {'tags': {'url': '/ajax/autocomplete/tags/base/basecontent/',
                                    'multiple': True,
                                    'multipleSeparator': " ",
                                    'size': 100}, }

    def add_owners(self, request, queryset, owners):
        if self.has_change_permission(request):
            selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
            n = queryset.count()
            obj_log = ugettext("Assigned owners")
            msg = "Successfully set owners for %d %s." % (n, model_ngettext(self.opts, n))
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
        if 'is_autolocated' in keys and\
           not request.user.has_perm('base.can_change_is_autolocated'):
            form.base_fields.pop('is_autolocated')
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
        db_fieldname = transmeta_aware_fieldname(db_field)
        if db_fieldname == 'description':
            field.widget.attrs['rows'] = 4
        return field

    def autogeolocalize_object(self, request, changelist, object_base_content):
        geolocate_object_base(object_base_content)

    def autogeolocalize_objects(self, request, changelist):
        objects_id = request.POST.getlist('selected')
        no_can_selected_objects = changelist.model.objects.filter(is_autolocated= False, location__main_location__isnull=False, id__in=objects_id)
        no_can_selected_objects_ids = ["%s"%ncso.id for ncso in no_can_selected_objects]
        set_no_can_selected_objects_ids = set(no_can_selected_objects_ids)
        set_objects_id = set(objects_id)
        objects_id = list(set_objects_id.difference(set_no_can_selected_objects_ids))
        if objects_id or no_can_selected_objects:
            if request.POST.get('post', False):
                changelist = get_changelist(request, self.model, self)
                objects_base_content = changelist.model.objects.filter(id__in=objects_id)
                for object_base_content in objects_base_content:
                    self.autogeolocalize_object(request, changelist, object_base_content)
                return ""
            extra_context = {'title': _('Are you sure you want geoautolocalized?'),
                             'action_submit': 'autogeolocalize_objects', 'no_can_selected_objects': no_can_selected_objects, 'no_can_selected_objects_message': _('These objects have a manual localization')}
            return self.confirm_action(request, objects_id, extra_context)
    autogeolocalize_objects.short_description = _("Autogeolocalize")


class BaseContentAdminExtra(BaseContentAdmin):
    change_list_template = 'admin/extra/change_list.html'
    list_display = BaseContentAdmin.list_display + ('class_name', )

    def changelist_view(self, request, extra_context=None):
        template_base = 'batchadmin/change_list.html'
        return super(BaseContentAdmin, self).changelist_view(request,
                                                             extra_context={'template_base': template_base,
                                                                            'admin_extra': True})


class ContactInfoAdmin(BaseAdmin):
    search_fields = ('contact_email', 'contact_email2', 'phone', 'phone2', 'fax', )


class RelatedModelAdmin(BaseAdmin):
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

    def changelist_view(self, request, extra_context=None):
        extra_context = self._update_extra_context(request, extra_context)
        return super(RelatedModelAdmin, self).changelist_view(request, extra_context)

    def queryset(self, request, basecontent=None):
        base_qs = super(RelatedModelAdmin, self).queryset(request)
        if basecontent is None:
            # we override our related content
            basecontent = self.basecontent
        return base_qs.filter(**{self.related_field: basecontent})

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self._update_extra_context(request, extra_context)
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
            if getattr(manager, 'through', None) is None:
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


class BaseContentRelatedModelAdmin(BaseAdmin, StatusControlProvider):
    selected = ''
    is_foreign_model = False

    def _update_extra_context(self, extra_context=None):
        extra_context = extra_context or {}
        basecontent_type_id = ContentType.objects.get_for_model(BaseContent).id
        extra_context.update({'basecontent': self.admin_site.basecontent,
                              'basecontent_opts': self.admin_site.basecontent._meta,
                              'basecontent_type_id': basecontent_type_id,
                              'inside_basecontent': True,
                              'is_foreign_model': self.is_foreign_model,
                              'no_location': getattr(self.admin_site, 'no_location', False),
                              'no_contact': getattr(self.admin_site, 'no_contact', False),
                              'selected': self.selected})
        return extra_context

    def has_add_permission(self, request):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        has_add_perm = super(BaseContentRelatedModelAdmin, self).has_add_permission(request)
        if has_add_perm:
            return True
        # we consider an user can add a related item of a content if can add this content
        model_admin = self.admin_site.model_admin
        if model_admin:
            return model_admin.has_add_permission(request)
        return False

    def has_change_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        has_change_perm = super(BaseContentRelatedModelAdmin, self).has_change_permission(request, obj)
        if has_change_perm:
            return True
        # we consider an user can add a related item of a content if can add this content
        model_admin = self.admin_site.model_admin
        basecontent = self.admin_site.basecontent
        if model_admin and basecontent:
            return model_admin.has_change_permission(request, basecontent)
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = self._update_extra_context(extra_context)
        return super(BaseContentRelatedModelAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = self._update_extra_context(extra_context)
        return super(BaseContentRelatedModelAdmin, self).change_view(request, object_id, extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context = self._update_extra_context(context)
        return super(BaseContentRelatedModelAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def delete_view(self, request, object_id, extra_context=None):
        extra_context = self._update_extra_context(extra_context)
        return super(BaseContentRelatedModelAdmin, self).delete_view(request, object_id, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        extra_context = self._update_extra_context(extra_context)
        return super(BaseContentRelatedModelAdmin, self).history_view(request, object_id, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        """
        Overrides Django admin behaviour
        """
        form = super(BaseContentRelatedModelAdmin, self).get_form(request, obj, **kwargs)
        if 'status' in form.base_fields.keys():
            user = request.user
            options = self._get_status_options(user, obj)
            if options:
                form.base_fields['status'].choices = options
                if 'pending' in [o[0] for o in options]:
                    form.base_fields['status'].initial = 'pending'
            else:
                form.base_fields.pop('status')

        return form


class VideoChecker(object):

    def get_form(self, request, obj=None):
        form = super(VideoChecker, self).get_form(request, obj)

        def clean(self):
            super(form, self).clean()
            file_cleaned_data = self.cleaned_data.get('file', None)
            url_cleaned_data = self.cleaned_data.get('external_url', None)
            old_file=obj and obj.file

            if not old_file and not url_cleaned_data and not file_cleaned_data:
                global_errors = self.errors.get('__all__', ErrorList([]))
                global_errors.extend(ErrorList([_(u'Please specify at least a video file or a video url')]))
                self._errors['__all__'] = ErrorList(global_errors)
            elif file_cleaned_data:
                extension = file_cleaned_data.name.split('.')[-1].lower()
                if extension not in ('flv', 'f4v'):
                    file_errors = self.errors.get('file', ErrorList([]))
                    file_errors.extend(ErrorList([_(u'Video file must be in flv format')]))
                    self._errors['file'] = ErrorList(file_errors)
            return self.cleaned_data
        form.clean = clean
        return form


class LocationModelAdminMixin(object):

    title_first_fieldset = None

    def set_fieldset(self):
        """Returns a BaseInlineFormSet class for use in admin add/change views."""
        render_message = ugettext('Click to Locate')
        adding = "<a name 'ajax_geolocation'>(<a href='#ajax_geolocation' class='ajax_geolocation'>%s</a>) <input id='id_input_ajax' type='text' class='input_ajax'><img id='img_ajax_loader' src='%simg/ajax-loader-transparent.gif' class='hide ajax_geolocation' />" % (render_message, settings.MEDIA_URL)

        title_fieldset = mark_safe("%s %s" % (ugettext(u'Location Maps'), adding))

        self.fieldsets = (
            (self.title_first_fieldset, {'fields': ('address', 'address_type', 'number', 'postal_code', 'address_more_info', 'cities')}),
            (title_fieldset,
                {'fields': ('main_location', 'main_altitude', 'gps_location', 'gps_altitude', 'borders', )}
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
        __media.add_js(['js/osmgeoadmin.latitude.longitude.js'])
        return __media
    media = property(_media)


class InlineLocationModelAdmin(LocationModelAdminMixin):

    def __init__(self, parent_model, admin_site):
        from merengue.places.admin import GoogleAdmin

        super(InlineLocationModelAdmin, self).__init__(parent_model, admin_site)
        self.geoModelAdmin = GoogleAdmin(parent_model, admin_site)
        self.geoModelAdmin.widget = OpenLayersInlineLatitudeLongitude
        self.geoModelAdmin.map_template = 'gis/admin/google_inline.html'

    def _media(self, *args, **kwargs):
        media_super = super(InlineLocationModelAdmin, self)._media(*args, **kwargs)
        media_geo = self.geoModelAdmin._media(*args, **kwargs)
        media_super.add_js(media_geo._js)
        media_super.add_css(media_geo._css)
        media_super.add_js(['js/osmgeoadmin.latitude.longitude.js'])
        return media_super
    media = property(_media)

    def get_formset(self, request, obj=None, **kwargs):
        """Returns a BaseInlineFormSet class for use in admin add/change views."""
        self.set_fieldset()
        return super(InlineLocationModelAdmin, self).get_formset(request, obj, **kwargs)

    def get_map_widget(self, *args, **kwargs):
        return self.geoModelAdmin.get_map_widget(*args, **kwargs)


class BaseContentRelatedLocationModelAdmin(LocationModelAdminMixin, BaseContentRelatedModelAdmin, OSMGeoAdminLatitudeLongitude):
    selected = 'location'
    is_foreign_model = True
    extra_js = [GMAP.api_url + GMAP.key]
    map_width = 500
    map_height = 300
    default_zoom = 10
    default_lat = 4500612.0
    default_lon = -655523.0
    map_template = 'gis/admin/google.html'
    title_first_fieldset = _('Address')

    def response_change(self, request, obj):
        super(BaseContentRelatedLocationModelAdmin, self).response_change(request, obj)
        return HttpResponseRedirect(self.admin_site.basecontent.get_admin_absolute_url())

    def response_add(self, request, obj):
        response = super(BaseContentRelatedLocationModelAdmin, self).response_add(request, obj)
        if response.get('location', 'location') == '../':
            post_url = self.admin_site.basecontent.get_admin_absolute_url()
            return HttpResponseRedirect(post_url)
        return response

    def save_model(self, request, obj, form, change):
        self.admin_site.basecontent.is_autolocated = False
        self.admin_site.basecontent.save()
        super(BaseContentRelatedLocationModelAdmin, self).save_model(request, obj, form, change)
        self.admin_site.basecontent.location = obj
        self.admin_site.basecontent.save()


class BaseContentRelatedContactInfoAdmin(BaseContentRelatedModelAdmin):
    selected = 'contact'
    is_foreign_model = True

    def response_change(self, request, obj):
        super(BaseContentRelatedContactInfoAdmin, self).response_change(request, obj)
        return HttpResponseRedirect(self.admin_site.basecontent.get_admin_absolute_url())

    def response_add(self, request, obj):
        response = super(BaseContentRelatedContactInfoAdmin, self).response_add(request, obj)
        if response.get('location', 'location') == '../':
            post_url = self.admin_site.basecontent.get_admin_absolute_url()
            return HttpResponseRedirect(post_url)
        return response

    def save_model(self, request, obj, form, change):
        super(BaseContentRelatedContactInfoAdmin, self).save_model(request, obj, form, change)
        self.admin_site.basecontent.contact_info = obj
        self.admin_site.basecontent.save()


class PublicTypeAdmin(BaseAdmin):
    search_fields = ('name_es', )


class SegmentAdmin(BaseAdmin):
    search_fields = ('name_es', )


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
        __media.add_js(['js/jquery-ui-1.5.3.custom.min.js'])
        if self.stacked_inline:
            __media.add_js(['js/menu-sort-stacked.js'])
        if self.tabular_inline:
            __media.add_js(['js/menu-sort-tabular.js'])
        return __media
    media = property(_media)


class BaseOrderableAdmin(BaseAdmin):
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


class LogEntryRelatedContentModelAdmin(admin.ModelAdmin):
    list_display = ('object_repr_slice', 'get_link_contenttype', 'img_is_addition',
                    'img_is_change', 'img_is_deletion', 'get_link_admin_url',
                    'get_link_public_url', 'action_time')

    change_list_template = 'admin/logentry/change_list.html'

    converter_status_in_document_status = {
                                            'draft': 1,
                                            'published': 2,
                                            'pending': None,
                                            'deleted_in_plone': None,
                                        }
    list_filter = ('content_type', )

    def changelist_view(self, request, extra_context=None):
        status = request.GET.get('status', None)
        content = request.GET.get('content_type__id__exact', None)
        try:
            if status:
                request_copy = copy_request(request, ['status'])
                if content:
                    objects_ids = []
                    list_models = [BaseMultimedia]
                    list_models.extend(Base.__subclasses__())
                    content = ContentType.objects.get(id=content)
                    for basemodel in list_models:
                        for model in basemodel.__subclasses__():
                            if content.model_class() == model:
                                objects_ids.extend([unicode(o.id) for o in model.objects.filter(status=status)])
                    document_status = self.converter_status_in_document_status[status]
                    if content.model_class() == Document:
                        objects_ids.extend([unicode(o.id) for o in Document.objects.filter(status=document_status)])
                    request_copy.GET['object_id__in'] = (',').join(objects_ids)
                    request_copy.GET['object_id__in'] = (',').join(objects_ids)
                else:
                    request.user.message_set.create(message=u"%s"%_('Select first a content type'))
            else:
                request_copy = request
            cl = ChangeList(request_copy, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        cl.has_filters=True
        status_list = settings.STATUS_LIST

        if status:
            if content:
                del cl.params['object_id__in']
            cl.params.update({'status': status})

        status_types = [{'name': _('All'), 'url': cl.get_query_string(remove='status')}]
        status_selected = _('All')
        for value, label in status_list:
            if status == value:
                status_selected = label
            status_types.append({'name': label,
                                'url': cl.get_query_string(new_params={'status': value})})

        return super(LogEntryRelatedContentModelAdmin, self).changelist_view(
                request=request_copy,
                extra_context={'has_add_permission': False,
                               'cl': cl,
                               'status_types': status_types,
                               'status_selected': status_selected,
                              },
                )

    def queryset(self, request):
        return LogEntry.objects.filter(user=self.admin_site.basecontent)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        return render_to_response('admin/logentry/change_form.html',
                                  context,
                                  context_instance=template.RequestContext(request))


class BaseContentLocateAdmin(BaseContentAdmin):
    """ Internal model admin for placing an content inside a base content object """
    list_display = ('name', 'get_icon_tag', 'class_name', 'get_cities_text',
                    'get_provinces_text', 'google_minimap', 'status', 'user_modification_date')
    list_filter = BaseContentAdmin.list_filter + ('class_name', )
    search_fields = ('name', )
    actions = ['place_at', ]
    change_list_template = 'admin/basecontent/locate_change_list.html'

    def __init__(self, placed_object_attr, *args, **kwargs):
        super(BaseContentLocateAdmin, self).__init__(*args, **kwargs)
        self.placed_object_attr = placed_object_attr
        if 'batchadmin_checkbox' in self.list_display:
            self.list_display.remove('batchadmin_checkbox')

    def queryset(self, request):
        # Do not return BaseContentAdmin.queryset
        # I need all basecontent objects to be placed
        return super(BaseContentAdmin, self).queryset(request)

    def set_placed_object(self, obj):
        """ set obj as placed object """
        self.placed_object = obj

    def has_change_permission(self, request, obj=None):
        opts = self.placed_object._meta
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
                if key not in (admin.ACTION_CHECKBOX_NAME, 'index'):
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
            extra_context = {'title': ugettext('Are you sure you want to place content at the following location?'),
                             'action_submit': 'place_at'}
            return self.confirm_action(request, [object_id], extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': _(u'Select where do you want to place the content')}
        return super(BaseContentLocateAdmin, self).changelist_view(request, extra_context)

    def place_at(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if queryset.count() == 1:
            obj = queryset[0]
            # we associate object selected to placed object
            setattr(self.placed_object, self.placed_object_attr, obj)
            self.placed_object.save()
            msg = ugettext(u"Content location set successfully.")
            self.message_user(request, msg)
            return HttpResponseRedirect('../../')
        else:
            msg = ugettext(u"Content location unchanged.")
            self.message_user(request, msg)
    place_at.short_description = "Place location at content"


class BaseContentLocateProvider(object):
    """ model admin that provide placing object functionality from placed object """

    change_form_template = 'admin/basecontent/locate_change_form.html'
    # field for associate object to another. You have to override this attribute
    placed_object_attr = 'basecontent_location'

    def __init__(self, *args, **kwargs):
        super(BaseContentLocateProvider, self).__init__(*args, **kwargs)
        # this will be out related admin for locating objects
        self.basecontent_admin = BaseContentLocateAdmin(self.placed_object_attr, BaseContent, self.admin_site)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        original = context.get('original', None)
        if original is not None:
            context.update({
                'content_location': getattr(original, self.placed_object_attr),
            })
        return super(BaseContentLocateProvider, self).render_change_form(
            request, context, add, change, form_url, obj,
        )

    def response_add(self, request, obj, post_url_continue='../%s/'):
        opts = obj._meta
        pk_value = obj._get_pk_val()

        msg = ugettext('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}

        if "_content_locate" in request.POST.keys():
            self.message_user(request, msg + u' ' + ugettext('You can select a content to place your location.'))
            return HttpResponseRedirect(post_url_continue % pk_value + 'content_locate/')
        return super(BaseContentLocateProvider, self).response_add(request, obj, post_url_continue)

    def __call__(self, request, url):
        if url and 'content_locate' in url:
            new_url = url[url.find('content_locate')+15:] or None
            object_id = url[:url.find('/content_locate')]
            try:
                if object_id == 'add':
                    self.basecontent_admin.set_placed_object(None)
                else:
                    obj = self.model._default_manager.get(pk=unquote(object_id))
                    self.basecontent_admin.set_placed_object(obj)
                # we delegate location to basecontent_admin
                return self.basecontent_admin(request, new_url)
            except self.model.DoesNotExist:
                pass
        elif url and url.endswith('content_unplace'):
            url = url[:url.find('/content_unplace')]
            return self.unplace(request, unquote(url))
        return super(BaseContentLocateProvider, self).__call__(request, url)

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

        content_location = getattr(obj, self.placed_object_attr)
        if request.method == 'POST':
            if content_location:
                setattr(obj, self.placed_object_attr, None)
                obj.save()
                msg = ugettext(u"Content is no longer placed at %s." % content_location)
                self.message_user(request, msg)
            return HttpResponseRedirect("../")
        else:
            return render_to_response('admin/basecontent/unplace.html',
                                      {'content': obj,
                                       'content_location': content_location},
                                      context_instance=template.RequestContext(request))


#### monkey patching ####

# Hago un poco de monkey patching para mostrar lo que quiero en LogEntryRelatedContentModelAdmin.
# atributo list_display


def get_url(self, admin=False, url=None, label=None):
    if not self.object_id.isdigit():
        return _('Error in id')
    if self.object_id and not url:
        try:
            object = self.content_type.model_class().objects.get(pk=self.object_id)
        except models.ObjectDoesNotExist:
            return _('deleted')
        try:
            if admin:
                url = '/admin/%s' %self.get_admin_url()
            else:
                try:
                    get_absolute_url = getattr(object, 'get_absolute_url', '')
                    url = get_absolute_url and get_absolute_url() or get_absolute_url
                except TypeError:
                    pass
            label = url
        except AttributeError:
            pass

    if url:
        if len(label) > 30:
            label = "%s ..." % label[:30]
        return mark_safe("<a href='%s'>%s</a>" % (url, label))
    return '---'


def get_link_admin_url(self):
    return self.get_url(True)
get_link_admin_url.allow_tags = True
get_link_admin_url.short_description = _('Admin url')


def get_link_public_url(self):
    return self.get_url(False)
get_link_public_url.allow_tags = True
get_link_public_url.short_description = _('Public url')


def get_link_contenttype(self):
    model_class = self.content_type.model_class()
    return self.get_url(url='/admin/%s/%s/'% (model_class._meta.app_label, model_class._meta.module_name), label=self.content_type.__unicode__())
get_link_contenttype.allow_tags = True
get_link_contenttype.short_description = _('Content type')


def get_img(self, value, text=''):
    if value:
        return mark_safe('<img alt="False" src="%simg/admin/icon-yes.gif"/> %s' % (settings.ADMIN_MEDIA_PREFIX, text))
    else:
        return mark_safe('<img alt="False" src="%simg/admin/icon-no.gif"/> %s' % (settings.ADMIN_MEDIA_PREFIX, text))


def img_is_addition(self):
    return self.get_img(self.is_addition())
img_is_addition.allow_tags = True
img_is_addition.short_description = _('Added')


def img_is_change(self):
    return self.get_img(self.is_change(), '<p>%s</p>' % self.change_message)
img_is_change.allow_tags = True
img_is_change.short_description = _('Changed')


def img_is_deletion(self):
    return self.get_img(self.is_deletion())
img_is_deletion.allow_tags = True
img_is_deletion.short_description = _('Deleted')


def object_repr_slice(self):
    if len(self.object_repr) < 40:
        return self.object_repr
    else:
        return "%s..." % self.object_repr[:40]

LogEntry.object_repr_slice = object_repr_slice
LogEntry.get_url = get_url
LogEntry.get_link_admin_url = get_link_admin_url
LogEntry.get_link_public_url = get_link_public_url
LogEntry.get_link_contenttype = get_link_contenttype
LogEntry.get_img = get_img
LogEntry.img_is_addition = img_is_addition
LogEntry.img_is_change = img_is_change
LogEntry.img_is_deletion = img_is_deletion


class BaseContentOwnedAdmin(BaseAdmin):
    change_list_template = 'admin/auth/user/owned_contents.html'
    actions = ['unassign_ownership']
    search_fields = ('name', )
    list_display = ('name', 'class_name', 'get_cities_text', 'get_provinces_text', 'google_minimap', 'status')
    list_filter = ('class_name', 'status')
    ordering = ('name', )
    base_user = None

    def _update_extra_context(self, extra_context=None):
        extra_context = extra_context or {}
        basecontent_type_id = ContentType.objects.get_for_model(BaseContent).id
        extra_context.update({'base_user': self.base_user,
                              'base_user_opts': self.base_user._meta,
                             })
        return extra_context

    def queryset(self, request):
        if not self.base_user:
            return BaseContent.objects.get_empty_queryset()
        else:
            return BaseContent.objects.filter(owners=self.base_user)

    def changelist_view(self, request, extra_context=None):
        extra_context = self._update_extra_context(extra_context)
        return super(BaseContentOwnedAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = self._update_extra_context(extra_context)
        changelist = get_changelist(request, self.model, self)
        post = request.POST.copy()
        post.update({'selected': object_id})
        request.POST = post
        redirect_to = '..'
        return self.unassign_ownership(request, changelist, redirect_to)

    def del_ownership(self, request, queryset, redirect_to):
        n = queryset.count()
        obj_log = ugettext(u"Unassigned ownership")
        msg_data = {'count': n,
                    'model_name': model_ngettext(self.opts, n)}
        msg = ugettext(u"Successfully unassigned ownership for %(count)d %(model_name)s.") % msg_data
        if n:
            for obj in queryset:
                obj.owners.remove(self.base_user)
                self.log_change(request, obj, obj_log)
            self.message_user(request, msg)
        if redirect_to:
            return HttpResponseRedirect(redirect_to)

    def unassign_ownership(self, request, queryset, redirect_to=None):
        if not self.has_change_permission(request):
            raise PermissionDenied
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            if request.POST.get('post', False):
                return self.del_ownership(request, queryset, redirect_to)
            extra_context = {'title': _(u'Are you sure you want to unassign ownership of these objects?'),
                             'action_submit': 'unassign_ownership'}
            return self.confirm_action(request, queryset, extra_context)
    unassign_ownership.short_description = _(u"Unassign ownership")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserAdmin(BaseAdmin, UserAdminOriginal):
    form = UserChangeFormCust
    add_form = UserCreationFormCust
    list_display = UserAdminOriginal.list_display + ('is_active', )
    list_filter = UserAdminOriginal.list_filter + ('is_active', )

    def __init__(self, model, admin_site):
        super(UserAdmin, self).__init__(model, admin_site)
        self.owned_contents_admin = BaseContentOwnedAdmin(BaseContent, admin_site)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        return super(BaseAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_context=None):
        return super(UserAdmin, self).change_view(request, object_id,
                                                  extra_context={'is_user_change_view': True})

    def __call__(self, request, url):
        if url and url.find('/owned')>=0:
            url = url.replace('/owned', '')
            try:
                user_id, url = url.split('/', 1)
            except:
                user_id = url
                url = None
            user_id = unquote(user_id)
            self.owned_contents_admin.base_user = User.objects.get(id=user_id)
            url = url or None
            return self.owned_contents_admin.__call__(request, url)
        else:
            return super(UserAdmin, self).__call__(request, url)


def register(site):
    ## register admin models
    site.register(User, UserAdmin)
    site.register(Group, GroupAdmin)
    site.register(BaseContent, BaseContentAdmin)
    site.register(ContactInfo, ContactInfoAdmin)


def setup_basecontent_admin(basecontent_admin_site):
    basecontent_admin_site.register(Location, BaseContentRelatedLocationModelAdmin)
