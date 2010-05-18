from merengue.base.admin import BaseAdmin

from merengue.perms.models import ObjectPermission
from merengue.perms.models import Permission
from merengue.perms.models import PrincipalRoleRelation
from merengue.perms.models import Role


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
        if change:
            for perm in Permission.objects.all():
                permissions.append((perm, perm.objectpermission_set.filter(role=obj) and True or False))
        else:
            permissions = [(perm, False) for perm in Permission.objects.all()]
        context['permissions'] = permissions
        return super(RoleAdmin, self).render_change_form(request, context, add, change, form_url, obj)


def register(site):
    site.register(ObjectPermission)
    site.register(Permission)
    site.register(Role, RoleAdmin)
    site.register(PrincipalRoleRelation)
