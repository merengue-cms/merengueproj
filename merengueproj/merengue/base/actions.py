"""
Built-in, globally-available admin actions.
"""

from django import template
from django.contrib.admin import helpers
from django.contrib.admin.util import model_ngettext
from django.db import router
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy, ugettext as _

from merengue.base.admin_utils import get_deleted_contents
from merengue.perms.exceptions import PermissionDenied


def delete_selected(modeladmin, request, queryset, bypass_django_permissions=False):
    """
    Default action which deletes the selected objects.

    This action first displays a confirmation page whichs shows all the
    deleteable objects, or, if the user has no permission one of the related
    childs (foreignkeys), a "permission denied" message.

    Next, it delets all selected objects and redirects back to the change list.
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Check that the user has delete permission for the actual model
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied(user=request.user)

    using = router.db_for_write(modeladmin.model)

    # Populate deletable_objects, a data structure of all related objects that
    # will also be deleted.
    (deletable_objects, objects_without_delete_perm, perms_needed, protected) = get_deleted_contents(queryset, opts, request.user, modeladmin.admin_site, using, bypass_django_permissions)

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.
    if request.POST.get('post'):
        if perms_needed or objects_without_delete_perm or protected:
            raise PermissionDenied(user=request.user)
        n = queryset.count()
        if n:
            for obj in queryset:
                obj_display = force_unicode(obj)
                modeladmin.log_deletion(request, obj, obj_display)
            queryset.delete()
            modeladmin.message_user(request, _('Successfully deleted %(count)d %(items)s.') % {
                'count': n, 'items': model_ngettext(modeladmin.opts, n),
            })
        # Return None to display the change list page again.
        return None

    if len(queryset) == 1:
        objects_name = force_unicode(opts.verbose_name)
    else:
        objects_name = force_unicode(opts.verbose_name_plural)

    if perms_needed or objects_without_delete_perm or protected:
        title = _('Cannot delete %(name)s') % {'name': objects_name}
    else:
        title = _('Are you sure?')

    context = {
        'title': title,
        'objects_name': objects_name,
        'deletable_objects': [deletable_objects],
        'objects_without_delete_perm': objects_without_delete_perm,
        'queryset': queryset,
        'perms_lacking': perms_needed,
        'protected': protected,
        'opts': opts,
        'root_path': modeladmin.admin_site.root_path,
        'app_label': app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }

    # Display the confirmation page
    return render_to_response(modeladmin.delete_selected_confirmation_template or [
        'admin/%s/%s/delete_selected_confirmation.html' % (app_label, opts.object_name.lower()),
        'admin/%s/delete_selected_confirmation.html' % app_label,
        'admin/delete_selected_confirmation.html',
    ], context, context_instance=template.RequestContext(request))

delete_selected.short_description = ugettext_lazy('Delete selected %(verbose_name_plural)s')


def related_delete_selected(modeladmin, request, queryset):
    return delete_selected(modeladmin, request, queryset, True)
related_delete_selected.short_description = ugettext_lazy('Delete selected %(verbose_name_plural)s')
