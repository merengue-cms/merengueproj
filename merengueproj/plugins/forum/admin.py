from django.contrib import admin

from merengue.base.admin import (BaseContentAdmin, RelatedModelAdmin,
                                 BaseCategoryAdmin)

from plugins.forum.models import Forum, ForumCategory, Thread, ForumThreadComment

from transmeta import get_fallback_fieldname


class ForumCategoryAdmin(BaseCategoryAdmin):
    pass


class ForumAdmin(BaseContentAdmin):
    removed_fields = ('map_icon', 'commentable', )


class ThreadRelatedAdmin(RelatedModelAdmin):
    html_fields = ('description', )
    removed_fields = ('map_icon', 'commentable', )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}
    related_field = 'forum'

    def remove_related_field_from_form(self, form):
        pass


class ForumThreadCommentRelatedAdmin(RelatedModelAdmin):
    related_field = 'thread'


def register(site):
    """ Merengue admin registration callback """
    site.register(ForumThreadComment, admin.ModelAdmin)
    site.register(ForumCategory, ForumCategoryAdmin)
    site.register(Forum, ForumAdmin)
    site.register_related(Thread, ThreadRelatedAdmin, related_to=Forum)
    site.register_related(ForumThreadComment, ForumThreadCommentRelatedAdmin, related_to=Thread)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(Forum)
