# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from merengue.perms.models import ObjectPermission, Permission, PrincipalRoleRelation, Role

from merengue.perms.forms import UserChangeForm, GroupForm, PrincipalRoleRelationForm
from merengue.perms.utils import add_role, remove_role


class PermissionAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super(PermissionAdmin, self).get_urls()
        # override objectpermissions root path
        my_urls = patterns('',
            (r'^(.+)/permissions/$', self.admin_site.admin_view(self.change_roles_permissions)))

        return my_urls + urls

    def _add_local_role(self, request):
        prr_form = PrincipalRoleRelationForm(data=request.POST)
        if prr_form.is_valid():
            prr_form.save()
        msg = _('The princial role relation was created successfully')
        return (msg, '.')

    def _update_role_permissions(self, request, obj):
        selected = request.POST.getlist('selected_perm')
        for obj_perm in ObjectPermission.objects.filter(content=obj):
            role_perm = "%s_%s" % (obj_perm.role.id, obj_perm.permission.id)
            if role_perm not in selected:
                obj_perm.delete()
        for role_perm in selected:
            role_id, perm_id = role_perm.split('_')
            role = Role.objects.get(id=role_id)
            perm = Permission.objects.get(id=perm_id)
            op, created = ObjectPermission.objects.get_or_create(role=role, permission=perm, content=obj)
        msg = _('The role permissions were changed successfully.')
        if '_roles_continue' in request.POST:
            url_redirect = '.'
        else:
            url_redirect = '../'
        return (msg, url_redirect)

    def _update_role_users(self, request, obj):
        selected = request.POST.getlist('selected_user')
        for ppr in PrincipalRoleRelation.objects.filter(content=obj):
            role_user = "%s_%s" % (ppr.role.id, ppr.user.id)
            if role_user not in selected:
                ppr.delete()
        for role_user in selected:
            role_id, user_id = role_user.split('_')
            role = Role.objects.get(id=role_id)
            user = User.objects.get(id=user_id)
            ppr, created = PrincipalRoleRelation.objects.get_or_create(role=role,
                                                                       user=user,
                                                                       content=obj)
        msg = _('The role users were changed successfully.')
        if '_users_continue' in request.POST:
            url_redirect = '.'
        else:
            url_redirect = '../'
        return (msg, url_redirect)

    def change_roles_permissions(self, request, object_id, extra_context=None):
        opts = self.model._meta
        admin_site = self.admin_site
        has_perm = request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())
        obj = get_object_or_404(self.model, pk=object_id)
        if request.method == 'POST':
            if '_continue_role_relation' in request.POST:
                msg, url_redirect = self._add_local_role(request)
            elif '_roles_continue' in request.POST or '_roles_save' in request.POST:
                msg, url_redirect = self._update_role_permissions(request, obj)
            elif '_users_continue' in request.POST or '_users_save' in request.POST:
                msg, url_redirect = self._update_role_users(request, obj)
            return self.response_change(request, msg, url_redirect)

        roles = Role.objects.all()
        role_permissions = {}

        for perm in self.get_permissions(obj):
            role_permissions[perm] = []
            for role in roles:
                role_permissions[perm].append((role, perm.objectpermission_set.filter(role=role, content=obj) and True or False))

        prr_form = PrincipalRoleRelationForm(initial={'content': obj.pk})
        pprs = PrincipalRoleRelation.objects.filter(content=obj)
        user_roles = {}
        for ppr in pprs:
            if not ppr.user in user_roles:
                user_roles[ppr.user] = []
            for role in roles:
                user_rol = (role, ppr.user.principalrolerelation_set.filter(role=role) and True or False)
                if not user_rol in user_roles[ppr.user]:
                    user_roles[ppr.user].append(user_rol)
        context = {'': obj,
                   'admin_site': admin_site.name,
                   'change': True,
                   'is_popup': False,
                   'save_as': False,
                   'has_delete_permission': False,
                   'has_add_permission': False,
                   'add': False,
                   'model_admin': self,
                   'title': "Roles permissions",
                   'opts': opts,
                   'root_path': '/%s' % admin_site.root_path,
                   'app_label': opts.app_label,
                   'has_change_permission': has_perm,
                   'role_permissions': role_permissions,
                   'roles': roles,
                   'form_url': '.',
                   'prr_form': prr_form,
                   'user_roles': user_roles}


        template = 'admin/perms/objectpermission/role_permissions.html'
        return render_to_response(template,
                                  context,
                                  context_instance=RequestContext(request))

    def response_change(self, request, msg=None, url_redirect=None, *args, **kwargs):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if not msg:
            msg = _('The role permissions was changed successfully.')
        if not url_redirect:
            if "_continue" in request.POST:
                url_redirect = request.path
            else:
                url_redirect = '../'
        self.message_user(request, msg + ' ' + _("You may edit it again below."))
        return HttpResponseRedirect(url_redirect)

    def get_permissions(self, obj):
        models = obj._meta.parents.keys() + [obj.__class__]
        content_types = [ContentType.objects.get_for_model(model) for model in models]
        permissions = Permission.objects.filter(Q(content_types__in=content_types) | Q(builtin=True))
        return permissions


class ObjectPermissionAdmin(PermissionAdmin):

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(PermissionAdmin, self).get_urls()
        # override objectpermissions root path
        my_urls = patterns('',
            (r'^$', self.admin_site.admin_view(self.change_roles_permissions)))

        return my_urls + urls

    def change_roles_permissions(self, request):

        opts = self.model._meta
        admin_site = self.admin_site
        has_perm = request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())

        if request.method == 'POST':
            selected = request.POST.getlist('selected_perm')
            for obj_perm in ObjectPermission.objects.filter(content__isnull=True):
                role_perm = "%s_%s" % (obj_perm.role.id, obj_perm.permission.id)
                if role_perm not in selected:
                    obj_perm.delete()

            for role_perm in selected:
                role_id, perm_id = role_perm.split('_')
                role = Role.objects.get(id=role_id)
                perm = Permission.objects.get(id=perm_id)
                op, created = ObjectPermission.objects.get_or_create(role=role, permission=perm, content=None)

            return self.response_change(request)


        roles = Role.objects.all()
        permissions = {}

        for perm in Permission.objects.all():
            permissions[perm] = []
            for role in roles:
                permissions[perm].append((role, perm.objectpermission_set.filter(role=role) and True or False))


        context = {'admin_site': admin_site.name,
                   'change': True,
                   'is_popup': False,
                   'save_as': False,
                   'has_delete_permission': False,
                   'has_add_permission': False,
                   'add': False,
                   'model_admin': self,
                   'title': "Roles permissions",
                   'opts': opts,
                   'root_path': '/%s' % admin_site.root_path,
                   'app_label': opts.app_label,
                   'has_change_permission': has_perm,
                   'role_permissions': permissions,
                   'roles': roles}


        template = 'admin/perms/objectpermission/role_permissions.html'
        return render_to_response(template,
                                  context,
                                  context_instance=RequestContext(request))


class RoleAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super(RoleAdmin, self).save_model(request, obj, form, change)
        selected = request.POST.getlist('selected_perm')
        ObjectPermission.objects.filter(role=obj, content__isnull=True).exclude(permission__id__in=selected).delete()
        for perm_id in selected:
            perm = Permission.objects.get(id=perm_id)
            op, created = ObjectPermission.objects.get_or_create(role=obj, permission=perm, content=None)
            if created:
                op.save()

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        permissions = []
        if request.method == 'POST':
            selected = request.POST.getlist('selected_perm')
            for perm in Permission.objects.all():
                    permissions.append((perm, unicode(perm.id) in selected))
        else:
            if change:
                for perm in Permission.objects.all():
                    permissions.append((perm, perm.objectpermission_set.filter(role=obj) and True or False))
            else:
                permissions = [(perm, False) for perm in Permission.objects.all()]
        context['permissions'] = permissions
        return super(RoleAdmin, self).render_change_form(request, context, add, change, form_url, obj)


class UserAdmin(DjangoUserAdmin):
    form = UserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups', )}),
        (_('Roles'), {'fields': ('roles', )}),
    )

    list_display = DjangoUserAdmin.list_display + ('is_active', )
    list_filter = DjangoUserAdmin.list_filter + ('is_active', )

    def save_model(self, request, obj, form, change):
        super(UserAdmin, self).save_model(request, obj, form, change)
        roles_id = request.POST.getlist('roles')
        for role in Role.objects.all():
            role = Role.objects.get(id=role.id)
            if unicode(role.id) in roles_id:
                add_role(obj, role)
            else:
                remove_role(obj, role)


class GroupAdmin(DjangoGroupAdmin):
    form = GroupForm
    add_form = GroupForm

    def save_model(self, request, obj, form, change):
        super(GroupAdmin, self).save_model(request, obj, form, change)
        roles_id = request.POST.getlist('roles')
        for role in Role.objects.all():
            role = Role.objects.get(id=role.id)
            if unicode(role.id) in roles_id:
                add_role(obj, role)
            else:
                remove_role(obj, role)


def register(site):
    site.register(ObjectPermission, ObjectPermissionAdmin)
    site.register(Permission, PermissionAdmin)
    site.register(Role, RoleAdmin)
    site.register(User, UserAdmin)
    site.register(Group, GroupAdmin)
