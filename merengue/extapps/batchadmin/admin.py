from django.contrib import admin
from django import template
from django.contrib.admin.util import quote
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.text import capfirst
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.contrib.admin.util import get_deleted_objects
from django.utils.translation import ugettext as _


from batchadmin.forms import ActionForm, checkbox, CHECKBOX_NAME
from batchadmin.util import model_format_dict, model_ngettext, get_changelist


class BatchModelAdmin(admin.ModelAdmin):
    change_list_template = "batchadmin/change_list.html"
    list_display = ['batchadmin_checkbox'] + list(admin.ModelAdmin.list_display)
    batch_actions = ['delete_selected']
    batch_actions_perms = {}
    batch_action_form = ActionForm
    actions_on_top = True
    actions_on_bottom = True

    def __init__(self, *args, **kwargs):
        """
        After initializing `admin.ModelAdmin`, ensure that `list_display`
        contains 'batchadmin_checkbox' and that `list_display_links` won't try
        to link the checkbox.

        """
        super(BatchModelAdmin, self).__init__(*args, **kwargs)
        if 'batchadmin_checkbox' not in self.list_display:
            self.list_display = list(self.list_display)
            self.list_display.insert(0, 'batchadmin_checkbox')
        if not self.list_display_links:
            for name in self.list_display:
                if name != 'batchadmin_checkbox':
                    self.list_display_links = [name]
                    break

    def batchadmin_checkbox(self, object):
        """A `list_display` column containing a checkbox widget."""
        return checkbox.render(CHECKBOX_NAME, unicode(object.pk))
    batchadmin_checkbox.short_description = mark_safe('&#x2713;')
    batchadmin_checkbox.allow_tags = True

    def delete_selected(self, request, changelist):
        if self.has_delete_permission(request):
            selected = request.POST.getlist(CHECKBOX_NAME)
            objects = changelist.get_query_set().filter(pk__in=selected)
            n = objects.count()
            if n:
                for obj in objects:
                    object_repr = unicode(obj)
                    self.log_deletion(request, obj, object_repr)
                objects.delete()
                self.message_user(request, "Successfully deleted %d %s." % (
                    n, model_ngettext(self.opts, n)))
    delete_selected.short_description = "Delete selected %(verbose_name_plural)s"

    def delete_view(self, request, objects_id=[], extra_context=None):
        "The 'delete' admin view for this model."
        if not isinstance(objects_id, list) and not isinstance(objects_id, tuple):
            # workaround to handle simple object deletion
            return super(BatchModelAdmin, self).delete_view(request, objects_id, extra_context)
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
            get_deleted_objects(deleted_objects[i], perms_needed, request.user, obj, opts, 1, self.admin_site)

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

    def delete_confirm(self, request, changelist):
        objects_id = request.POST.getlist('selected')
        if objects_id:
            if request.POST.get('post'):
                changelist = get_changelist(request, self.model, self)
                return self.delete_selected(request, changelist)
            return self.delete_view(request, objects_id)
    delete_confirm.short_description = _("Delete confirm")

    def _get_batchadmin_choices(self):
        actions = getattr(self, 'batch_actions', [])
        choices = []
        for action in actions:
            func = getattr(self, action)
            description = getattr(func, 'short_description', None)
            if description is None:
                description = capfirst(action.replace('_', ' '))
            choice = (action, description % model_format_dict(self.opts))
            choices.append(choice)
        return choices
    batchadmin_choices = property(_get_batchadmin_choices)

    def batchadmin_dispatch(self, request, changelist, action):
        """
        Get the batch action named `action` and call it with `request` and
        `changelist` as arguments. `action` must be a callable attribute on
        the `BatchModelAdmin` instance.

        """
        perm_needed = self.batch_actions_perms.get(action, None)
        if perm_needed and not request.user.has_perm(perm_needed):
                raise PermissionDenied
        action_func = getattr(self, action, None)
        if callable(action_func):
            return action_func(request, changelist)

    def get_available_choices_for_user(self, user):
        choices = self.batchadmin_choices
        new_choices=[]
        for (choice, label) in choices:
            perm_needed = self.batch_actions_perms.get(choice, None)
            if not perm_needed or user.has_perm(perm_needed):
                new_choices.append((choice, label))
        return new_choices

    def changelist_view(self, request, extra_context=None):
        """
        Render the change list with checkboxes for each object and a menu
        for performing batch actions. Submitting the action form POSTs back
        to this view, where it is dispatched to the appropriate handler.

        """
        choices = self.get_available_choices_for_user(request.user)
        if request.method == 'POST':
            changelist = get_changelist(request, self.model, self)

            # There can be multiple action forms on the page (at the top
            # and bottom of the change list, for example). Get the action
            # whose button was pushed.
            action_index = 0
            action_index_name = 'index'
            for key in request.POST.keys():
                if key.startswith('index-'):
                    action_index_name = key
                    try:
                        action_index = int(key[6:])
                    except:
                        action_index = 0
                    break
            data = {}
            for key in request.POST:
                if key not in (CHECKBOX_NAME, action_index_name):
                    data[key] = request.POST.getlist(key)[action_index]
            action_form = self.batch_action_form(data, auto_id=None)
            action_form.fields['action'].choices = choices

            if action_form.is_valid():
                action = action_form.cleaned_data['action']
                response = self.batchadmin_dispatch(request, changelist, action)
                if isinstance(response, HttpResponse):
                    return response
                else:
                    redirect_to = request.META.get('HTTP_REFERER') or "."
                    return HttpResponseRedirect(redirect_to)
        else:
            action_form = self.batch_action_form(auto_id=None)
            action_form.fields['action'].choices = choices
        context = {
            'batchadmin_action_form': action_form,
            'batchadmin_media': action_form.media,
            'batchadmin_on_top': self.actions_on_top,
            'batchadmin_on_bottom': self.actions_on_bottom,
        }
        context.update(extra_context or {})
        return super(BatchModelAdmin, self).changelist_view(request, context)

    def confirm_action(self, request, objects_id=[], extra_context=None,
                       confirm_template="batchadmin/confirm_action.html"):
        "The 'confirm action admin view"

        if not objects_id:
            objects_id = []

        opts = self.model._meta
        app_label = opts.app_label
        selected_objects = []
        context = {}
        for i, object_id in enumerate(objects_id):
            try:
                obj = self.model._default_manager.get(pk=object_id)
            except self.model.DoesNotExist:
                # Don't raise Http404 just yet, because we haven't checked
                # permissions yet. We don't want an unauthenticated user to be able
                # to determine whether a given object exists.
                obj = None

            if not self.has_change_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                raise Http404('%s object with primary key %r does not exist.' % (force_unicode(opts.verbose_name), escape(object_id)))

            # Populate highlight_objects, a data structure of all related objects that
            # will also be deleted.
            selected_objects.append([mark_safe(u'<input class="batch-select" type="checkbox" name="selected" value="%s" checked="true"/>%s: %s' % (quote(object_id), escape(force_unicode(capfirst(opts.verbose_name))), escape(obj))), []])

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
                "objects_id": objects_id,
            }
            context.update(extra_context or {})

        return render_to_response(confirm_template,
                                  context,
                                  context_instance=template.RequestContext(request))
