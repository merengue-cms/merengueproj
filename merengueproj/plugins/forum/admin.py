from django.contrib import admin

from merengue.base.admin import (BaseContentAdmin, RelatedModelAdmin,
                                 BaseCategoryAdmin)
from merengue.section.admin import SectionContentAdmin

from plugins.forum.models import Forum, ForumCategory, Thread, ForumThreadComment

from transmeta import get_fallback_fieldname


class ForumCategoryAdmin(BaseCategoryAdmin):
    pass


class ForumAdmin(BaseContentAdmin):
    removed_fields = ('map_icon', 'commentable', )


class ForumSectionAdmin(ForumAdmin, SectionContentAdmin):
    manage_contents = True


class ThreadRelatedAdmin(BaseContentAdmin, RelatedModelAdmin):
    html_fields = ('description', )
    removed_fields = ('map_icon', 'commentable', )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}
    related_field = 'forum'

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            form = super(RelatedModelAdmin, self).get_form(request, obj, **kwargs)
        else:
            form = super(ThreadRelatedAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_form(self, request, form, change):
        if not change:
            form.instance.user = request.user
        if not self.related_field in form.base_fields.keys():
            form.cleaned_data[self.related_field] = self.basecontent
        return super(RelatedModelAdmin, self).save_form(request, form, change)

    def response_change(self, request, obj):
        if '_continue' in request.POST.keys():
            # we need change request.path because manager may change the forum
            # of this thread, and then you have to redirect to the new
            # forum->thread related admin (see #997)
            request.path = obj.get_admin_absolute_url()
        return super(ThreadRelatedAdmin, self).response_change(request, obj)


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
