from merengue.base.admin import BaseContentAdmin, RelatedModelAdmin

from plugins.forum.models import Forum, Thread


class ForumAdmin(BaseContentAdmin):
    removed_fields = ('commentable', )
    html_fields = ('description', )


class ThreadRelatedAdmin(RelatedModelAdmin):
    html_fields = ('description', )
    removed_fields = ('commentable', )
    related_field = 'forum'


def register(site):
    """ Merengue admin registration callback """
    site.register(Forum, ForumAdmin)
    site.register_related(Thread, ThreadRelatedAdmin, related_to=Forum)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Forum)
