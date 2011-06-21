from django.contrib.admin.util import NestedObjects, quote
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.encoding import force_unicode

from merengue.base.models import BaseContent
from merengue.perms.models import ObjectPermission


class NestedContents(NestedObjects):
    pass


def get_deleted_contents(objs, opts, user, admin_site, using, bypass_django_perms=False):
    """
    This is a copy of django.contrib.admin.util.get_deleted_objects.

    We have changed only the NestedContents class, because Django admin does not
    allow to redefine one. See http://code.djangoproject.com/ticket/15140
    """
    collector = NestedContents(using=using)
    collector.collect(objs)

    # TODO This next bit is needed only because GenericRelations are
    # cascade-deleted way down in the internals in
    # DeleteQuery.delete_batch_related, instead of being found by
    # _collect_sub_objects. Refs #12593.
    from django.contrib.contenttypes import generic
    first_obj = objs[0]
    for f in first_obj._meta.many_to_many:
        if isinstance(f, generic.GenericRelation):
            rel_manager = f.value_from_object(first_obj)
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
                              first_obj.__class__, first_obj)

    def format_callback(obj):
        is_managed_content = isinstance(obj, BaseContent)
        has_admin = obj.__class__ in admin_site._registry or is_managed_content
        opts = obj._meta
        if has_admin and not isinstance(obj, ObjectPermission):
            try:
                admin_url = reverse('%s:%s_%s_change'
                                    % (admin_site.name,
                                    opts.app_label,
                                    opts.object_name.lower()),
                                    None, (quote(obj._get_pk_val()), ))
            except NoReverseMatch:
                admin_url = ''
            p = '%s.%s' % (opts.app_label,
                        opts.get_delete_permission())
            if is_managed_content or hasattr(obj, 'can_delete'):
                if is_managed_content:
                    obj = obj.get_real_instance()
                if not obj.can_delete(user):  # maybe is not a BaseContent but implements can_delete
                    objects_without_delete_perm.add(obj)
            elif not bypass_django_perms and not user.has_perm(p):
                perms_needed.add(opts.verbose_name)
            # Display a link to the admin page.
            if admin_url:
                return mark_safe(u'%s: <a href="%s">%s</a>' %
                                 (escape(capfirst(opts.verbose_name)),
                                  admin_url,
                                  escape(obj)))
            else:
                return u'%s: %s' % (capfirst(opts.verbose_name),
                                    force_unicode(obj))
        else:
            # Don't display link to edit, because it either has no
            # admin or is edited inline.
            return u'%s: %s' % (capfirst(opts.verbose_name),
                                force_unicode(obj))

    perms_needed = set()
    objects_without_delete_perm = set()

    to_delete = collector.nested(format_callback)

    protected = [format_callback(obj) for obj in collector.protected]

    return to_delete, objects_without_delete_perm, perms_needed, protected
