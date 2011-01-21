from django.contrib.admin.util import NestedObjects, quote
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.encoding import force_unicode

from merengue.base.models import BaseContent
from merengue.perms.models import ObjectPermission
from merengue.perms.utils import has_permission


class NestedContents(NestedObjects):
    pass


def get_deleted_contents(objs, opts, user, admin_site, levels_to_root=4):
    """
    This is a copy of django.contrib.admin.util.get_deleted_objects.

    We have changed only the NestedContents class, because Django admin does not
    allow to redefine one. See http://code.djangoproject.com/ticket/15140
    """
    collector = NestedContents()
    for obj in objs:
        # TODO using a private model API!
        obj._collect_sub_objects(collector)

    # TODO This next bit is needed only because GenericRelations are
    # cascade-deleted way down in the internals in
    # DeleteQuery.delete_batch_related, instead of being found by
    # _collect_sub_objects. Refs #12593.
    from django.contrib.contenttypes import generic
    for f in obj._meta.many_to_many:
        if isinstance(f, generic.GenericRelation):
            rel_manager = f.value_from_object(obj)
            for related in rel_manager.all():
                # There's a wierdness here in the case that the
                # generic-related object also has FKs pointing to it
                # from elsewhere. DeleteQuery does not follow those
                # FKs or delete any such objects explicitly (which is
                # probably a bug). Some databases may cascade those
                # deletes themselves, and some won't. So do we report
                # those objects as to-be-deleted? No right answer; for
                # now we opt to report only on objects that Django
                # will explicitly delete, at risk that some further
                # objects will be silently deleted by a
                # referential-integrity-maintaining database.
                collector.add(related.__class__, related.pk, related,
                              obj.__class__, obj)

    perms_needed = set()
    objects_without_delete_perm = set()

    to_delete = collector.nested(_format_callback,
                                 user=user,
                                 admin_site=admin_site,
                                 levels_to_root=levels_to_root,
                                 objects_without_delete_perm=objects_without_delete_perm,
                                 perms_needed=perms_needed)

    return to_delete, objects_without_delete_perm, perms_needed


def _format_callback(obj, user, admin_site, levels_to_root, objects_without_delete_perm, perms_needed):
    is_managed_content = isinstance(obj, BaseContent)
    has_admin = obj.__class__ in admin_site._registry or is_managed_content
    opts = obj._meta
    try:
        admin_url = reverse('%s:%s_%s_change'
                            % (admin_site.name,
                               opts.app_label,
                               opts.object_name.lower()),
                            None, (quote(obj._get_pk_val()), ))
    except NoReverseMatch:
        admin_url = '%s%s/%s/%s/' % ('../'*levels_to_root,
                                     opts.app_label,
                                     opts.object_name.lower(),
                                     quote(obj._get_pk_val()))
    if has_admin and not isinstance(obj, ObjectPermission):
        p = '%s.%s' % (opts.app_label,
                       opts.get_delete_permission())
        if is_managed_content:
            obj = obj.get_real_instance()
            if not has_permission(obj, user, 'delete'):
                objects_without_delete_perm.add(obj)
        elif not user.has_perm(p):
            perms_needed.add(opts.verbose_name)
        # Display a link to the admin page.
        return mark_safe(u'%s: <a href="%s">%s</a>' %
                         (escape(capfirst(opts.verbose_name)),
                          admin_url,
                          escape(obj)))
    else:
        # Don't display link to edit, because it either has no
        # admin or is edited inline.
        return u'%s: %s' % (capfirst(opts.verbose_name),
                            force_unicode(obj))
