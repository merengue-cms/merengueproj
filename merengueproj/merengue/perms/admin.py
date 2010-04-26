from merengue.perms.models import ObjectPermission
from merengue.perms.models import Permission
from merengue.perms.models import PrincipalRoleRelation
from merengue.perms.models import Role


def register(site):
    site.register(ObjectPermission)
    site.register(Permission)
    site.register(Role)
    site.register(PrincipalRoleRelation)
