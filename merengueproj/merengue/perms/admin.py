from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.models import User, Group

from merengue.base.admin import BaseAdmin
from merengue.perms.models import ObjectPermission
from merengue.perms.models import Permission
from merengue.perms.models import PrincipalRoleRelation
from merengue.perms.models import Role
from merengue.perms.forms import UserChangeForm, GroupForm
from merengue.perms.utils import add_role, remove_role


class ObjectPermissionAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(ObjectPermissionAdmin, self).get_urls()
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

    def response_change(self, request):
        """
        Determines the HttpResponse for the change_view stage.
        """

        msg = _('The role permissions was changed successfully.')
        if "_continue" in request.POST:
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            return HttpResponseRedirect("../")


class RoleAdmin(BaseAdmin):

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
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups', )}),
        (_('Roles'), {'fields': ('roles', )}),
    )

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


class PermissionAdmin(BaseAdmin):
    pass


class PrincipalRoleRelationAdmin(BaseAdmin):
    pass


def register(site):
    site.register(ObjectPermission, ObjectPermissionAdmin)
    site.register(Permission, PermissionAdmin)
    site.register(Role, RoleAdmin)
    site.register(PrincipalRoleRelation, PrincipalRoleRelationAdmin)
    site.unregister(User)
    site.register(User, UserAdmin)
    site.unregister(Group)
    site.register(Group, GroupAdmin)
