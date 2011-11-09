# Copyright (c) 2010 by Yaco Sistemas <precio@yaco.es>
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django import template
from django.conf import settings
from django.contrib.admin.filterspecs import FilterSpec
from django.contrib.admin.util import unquote
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.encoding import force_unicode
from django.utils.functional import update_wrapper
from django.utils.html import escape
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from merengue.base.admin import RelatedModelAdmin, BaseAdmin, set_field_read_only
from merengue.base.models import BaseContent
from merengue.perms import utils as perms_api
from merengue.perms.exceptions import PermissionDenied
from merengue.perms.models import Permission, Role
from merengue.workflow import DEFAULT_WORKFLOW
from merengue.workflow.filterspecs import WorkflowModelRelatedFilterSpec
from merengue.workflow.models import (Workflow, State, Transition,
                                      WorkflowPermissionRelation,
                                      StatePermissionRelation,
                                      WorkflowModelRelation)
from merengue.workflow.utils import workflow_by_model, update_objects_permissions

from transmeta import get_fallback_fieldname


# Don't call register but insert it at the beginning of the registry
# otherwise, the AllFilterSpec will be taken first
FilterSpec.filter_specs.insert(0, (lambda f: f.name == 'workflow:workflowmodelrelation',
                               WorkflowModelRelatedFilterSpec))


class WorkflowAdmin(BaseAdmin):
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):

            def wrapper(*args, **kwargs):
                #kwargs['model_admin'] = self
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urls = super(WorkflowAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^update_permissions/$', wrap(self.update_permissions_view),
                name='update_permissions'),
            (r'^(?P<workflow_id>\d+)/graphic_workflow/$', wrap(self.graphic_workflow_view)))
        return my_urls + urls

    def object_tools(self, request, mode, url_prefix):
        tools = super(WorkflowAdmin, self).object_tools(request, mode, url_prefix)
        if mode == 'list':
            tools = [{'url': url_prefix + 'update_permissions/', 'label': ugettext('Update permissions'), 'class': 'default', 'permission': 'change'}] + tools
        elif mode == 'change':
            tools = [{'url': url_prefix + 'graphic_workflow/', 'label': ugettext('Graphic workflow'), 'class': 'default', 'permission': 'change'}] + tools
        return tools

    def has_delete_permission(self, request, obj=None):
        if obj and obj.slug == DEFAULT_WORKFLOW:
            return False
        elif obj:
            return True
        else:
            if request.method == 'POST' and \
               request.POST.get('action', None) == u'delete_selected':
                selected_objs = [Workflow.objects.get(id=int(key))
                                 for key in request.POST.getlist('_selected_action')]
                for sel_obj in selected_objs:
                    if not self.has_delete_permission(request, sel_obj):
                        return False
                return True
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super(WorkflowAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['initial_state'].queryset = obj.states.all()
            if obj.slug == DEFAULT_WORKFLOW:
                set_field_read_only(form.base_fields['slug'], 'slug', obj)
        elif 'initial_state' in form.base_fields.keys():
            del form.base_fields['initial_state']
        return form

    def update_permissions_view(self, request, extra_context=None):
        extra_context = self._base_update_extra_context(extra_context)
        if request.method == 'POST':
            update_objects_permissions()
            return HttpResponseRedirect('..')
        return render_to_response('admin/workflow/update_permissions.html',
                                  extra_context,
                                  context_instance=template.RequestContext(request, current_app=self.admin_site.name))

    def graphic_workflow_view(self, request, workflow_id, extra_context=None):
        workflow = get_object_or_404(Workflow, id=workflow_id)
        pairs = []
        transitions = {}
        for transition in workflow.transitions.all():
            for origin in transition.states.all():
                pair = origin.name, transition.destination.name
                if (pair[1], pair[0]) in pairs:
                    transitions[(pair[1], pair[0])] = '%s / %s' % (transitions[(pair[1], pair[0])],
                                                                   transition.name)
                elif not pair in pairs:
                    pairs.append(pair)
                    transitions[pair] = transition.name
        tmp_pairs, pairs = pairs[:], []
        pairs = [(pair[0], pair[1], transitions[pair]) for pair in tmp_pairs]
        context = extra_context or {}
        context.update({'pairs': pairs,
                        'original': workflow,
                        'title': unicode(workflow)})
        return render_to_response(
            'admin/workflow/graphic_workflow.html',
            context, context_instance=template.RequestContext(
                request, current_app=self.admin_site.name))


class StateRelatedModelAdmin(RelatedModelAdmin):
    tool_name = 'states'
    tool_label = _('states')
    related_field = 'workflow'
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}

    def has_delete_permission(self, request, obj=None):
        if obj and obj.slug in settings.STATIC_WORKFLOW_DATA['states']:
            return False
        elif obj:
            return True
        else:
            if request.method == 'POST' and \
               request.POST.get('action', None) == u'delete_selected':
                selected_objs = [State.objects.get(id=int(key))
                                 for key in request.POST.getlist('_selected_action')]
                for sel_obj in selected_objs:
                    if not self.has_delete_permission(request, sel_obj):
                        return False
                return True
        return False

    def get_urls(self):
        from django.conf.urls.defaults import patterns

        def wrap(view):

            def wrapper(*args, **kwargs):
                #kwargs['model_admin'] = self
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urls = super(StateRelatedModelAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^([^/]+)/permissions/$', wrap(self.permissions_view)))
        return my_urls + urls

    def get_form(self, request, obj=None, **kwargs):
        form = super(StateRelatedModelAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            workflow = obj.workflow
            form.base_fields['transitions'].queryset = Transition.objects.filter(workflow=workflow)
            if obj.slug in settings.STATIC_WORKFLOW_DATA['states']:
                set_field_read_only(form.base_fields['slug'], 'slug', obj)
        else:
            form.base_fields['transitions'].queryset = self.basecontent.transitions.all()
        return form

    def object_tools(self, request, mode, url_prefix):
        tools = super(StateRelatedModelAdmin, self).object_tools(request, mode, url_prefix)
        if mode == 'change':
            tools = [{'url': url_prefix + 'permissions/', 'label': ugettext('Permissions'), 'class': 'permissions', 'permission': 'change'}] + tools
        return tools

    def permissions_view(self, request, object_id, extra_context=None, parent_model_admin=None, parent_object=None):
        extra_context = self._update_extra_context(request, extra_context, parent_model_admin, parent_object)
        state = get_object_or_404(State, id=object_id)
        roles = Role.objects.all()
        permissions = [i.permission for i in parent_object.workflowpermissionrelation_set.all()]

        if request.method == 'POST':
            state_perms = request.POST.getlist('selected_perm')
            for perm in permissions:
                for role in roles:
                    rel_id = '%s_%s' % (role.id, perm.id)
                    if rel_id in state_perms:
                        StatePermissionRelation.objects.get_or_create(role=role, permission=perm, state=state)
                    else:
                        StatePermissionRelation.objects.filter(permission=perm, role=role, state=state).delete()
            msg = ugettext('State permissions were saved successfully. To make your changes effective you have to update permissions <a href="%(url)s">here</a>') \
                  % {'url': reverse('admin:update_permissions')}
            self.message_user(request, msg)
            return HttpResponseRedirect('..')

        role_permissions = {}
        for perm in permissions:
            role_permissions[perm] = []
            for role in roles:
                role_permissions[perm].append((role, StatePermissionRelation.objects.filter(role=role, permission=perm, state=state) and True or False))
        context = {
            'roles': roles,
            'role_permissions': role_permissions,
            'model_admin': self,
            'original': state,
            'title': _(u'Manage state permissions'),
        }
        context.update(extra_context)
        return render_to_response('admin/workflow/state_permissions.html',
                                  context,
                                  context_instance=template.RequestContext(request, current_app=self.admin_site.name))


class TransitionRelatedModelAdmin(RelatedModelAdmin):
    tool_name = 'transitions'
    tool_label = _('transitions')
    related_field = 'workflow'
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}

    def has_delete_permission(self, request, obj=None):
        if obj and obj.slug in settings.STATIC_WORKFLOW_DATA['transitions']:
            return False
        elif obj:
            return True
        else:
            if request.method == 'POST' and \
               request.POST.get('action', None) == u'delete_selected':
                selected_objs = [Transition.objects.get(id=int(key))
                                 for key in request.POST.getlist('_selected_action')]
                for sel_obj in selected_objs:
                    if not self.has_delete_permission(request, sel_obj):
                        return False
                return True
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super(TransitionRelatedModelAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            workflow = obj.workflow
            form.base_fields['destination'].queryset = State.objects.filter(workflow=workflow)
            if obj.slug in settings.STATIC_WORKFLOW_DATA['transitions']:
                set_field_read_only(form.base_fields['slug'], 'slug', obj)
        else:
            form.base_fields['destination'].queryset = self.basecontent.states.all()
        return form


class PermissionRelatedModelAdmin(RelatedModelAdmin):
    tool_name = 'permissions'
    tool_label = _('permissions')

    change_list_template = 'admin/workflow/workflow_permissions.html'

    def queryset(self, request, basecontent=None):
        return Permission.objects.all()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return perms_api.can_manage_site(request.user)

    def change_view(self, request, object_id, extra_context=None, parent_model_admin=None, parent_object=None):
        return HttpResponseRedirect('..')

    def changelist_view(self, request, extra_context=None, parent_model_admin=None, parent_object=None):
        extra_context = self._update_extra_context(request, extra_context, parent_model_admin, parent_object)
        permissions = self.queryset(request)
        if request.method == 'POST':
            wperms = request.POST.getlist('workflowpermission')
            for perm in permissions:
                if str(perm.id) in wperms:
                    WorkflowPermissionRelation.objects.get_or_create(permission=perm, workflow=self.basecontent)
                    perm.managed = True
                else:
                    WorkflowPermissionRelation.objects.filter(permission=perm, workflow=self.basecontent).delete()
                    perm.managed = False
            msg = ugettext('Workflow permissions were saved successfully.')
            self.message_user(request, msg)
        else:
            for perm in permissions:
                perm.managed = WorkflowPermissionRelation.objects.filter(permission=perm, workflow=self.basecontent).count()
        context = {
            'actions_on_top': True,
            'permissions': permissions,
            'title': _(u'Manage workflow permissions'),
            }
        context.update(extra_context)
        return render_to_response(self.change_list_template,
                                  context,
                                  context_instance=template.RequestContext(request, current_app=self.admin_site.name))


class ContentTypeRelatedModelAdmin(RelatedModelAdmin):
    tool_name = 'models'
    tool_label = _('models')
    inherit_actions = False
    list_display = ('__unicode__', 'is_related', 'current_workflow')
    list_filter = ('workflowmodelrelation', )
    actions = ['relate_model', 'unrelate_model']

    #change_list_template = 'admin/workflow/workflow_models.html'

    def current_workflow(self, obj):
        return workflow_by_model(obj.model_class())
    current_workflow.short_description = _(u"Current workflow")

    def is_related(self, obj):
        return WorkflowModelRelation.objects.filter(content_type=obj, workflow=self.basecontent).count()
    is_related.boolean = True
    is_related.short_description = _(u"Related to this workflow")

    def relate_model(self, request, queryset):
        if request.POST.get('post', False):
            for item in queryset:
                self.basecontent.set_to_model(item)
            self.message_user(request, ugettext(u'The workflow has been added to these models'))
        else:
            extra_context = {'title': ugettext(u'Are you sure you want to add the current workflow to these models?'),
                             'action_submit': 'relate_model'}
            return self.confirm_action(request, queryset, extra_context)
    relate_model.short_description = _(u"Add current workflow to selected models")

    def unrelate_model(self, request, queryset):
        if request.POST.get('post', False):
            for item in queryset:
                WorkflowModelRelation.objects.filter(content_type=item, workflow=self.basecontent).delete()
            self.message_user(request, ugettext(u'The workflow has been removed from these models'))
        else:
            extra_context = {'title': ugettext(u'Are you sure you want to remove the current workflow from these models?'),
                             'action_submit': 'unrelate_model'}
            return self.confirm_action(request, queryset, extra_context)
    unrelate_model.short_description = _(u"Remove current workflow from selected models")

    def lookup_allowed(self, lookup, value):
        if lookup == 'workflowmodelrelation__workflow':
            return True
        return super(ContentTypeRelatedModelAdmin, self).lookup_allowed(lookup, value)

    def queryset(self, request, basecontent=None):
        # Ugly hack to quickly extract non related content types
        if request.GET.get('id__isnull', None) == 'false':
            return ContentType.objects.exclude(workflowmodelrelation__workflow=self.basecontent)
        else:
            models = [BaseContent] + BaseContent.get_subclasses()
            return ContentType.objects.filter(model__in=[model._meta.module_name
                                                         for model in models])

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return perms_api.can_manage_site(request.user)

    def change_view(self, request, object_id, extra_context=None, parent_model_admin=None, parent_object=None):
        if request.method == 'POST':
            object_ids = request.POST.getlist('_selected_action')
        else:
            object_ids = [object_id]
        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied(content=obj,
                                   user=request.user,
                                   perm=perms_api.MANAGE_SITE_PERMISION)

        if obj is None or (object_ids and object_ids != [object_id]):
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(self.model._meta.verbose_name), 'key': escape(object_id)})
        queryset = self.queryset(request).filter(id__in=object_ids)

        if request.method == 'POST':
            if not object_ids:
                return HttpResponseRedirect("..")
            if request.POST.get('action', None) == 'relate_model':
                self.relate_model(request, queryset)
            else:
                self.unrelate_model(request, queryset)
            return HttpResponseRedirect("..")
        else:
            if self.is_related(obj):
                extra_context = {'title': ugettext(u'Are you sure you want to remove the current workflow from these models?'),
                                 'action_submit': 'unrelate_model'}
            else:
                extra_context = {'title': ugettext(u'Are you sure you want to add the current workflow to these models?'),
                                 'action_submit': 'relate_model'}
            return self.confirm_action(request, queryset, extra_context)


def register_related(site):
    site.register_related(State, StateRelatedModelAdmin, related_to=Workflow)
    site.register_related(Transition, TransitionRelatedModelAdmin, related_to=Workflow)
    site.register_related(Permission, PermissionRelatedModelAdmin, related_to=Workflow)
    site.register_related(ContentType, ContentTypeRelatedModelAdmin, related_to=Workflow)


def register(site):
    site.register(Workflow, WorkflowAdmin)
    register_related(site)
