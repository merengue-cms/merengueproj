# Copyright (c) 2010 by Yaco Sistemas
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

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.db.models import Q
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from merengue.base.admin import (OrderableRelatedModelAdmin, BaseContentAdmin, BaseAdmin,
                                 WorkflowBatchActionProvider, RelatedModelAdmin)
from merengue.base.models import BaseContent, MultimediaRelation
from merengue.multimedia.forms import AudioCheckerModelForm, VideoCheckerModelForm
from merengue.multimedia.models import (Photo, Video, PanoramicView, Image3D,
                                        File, Audio, BaseMultimedia)
from merengue.perms import utils as perms_api
from merengue.perms.exceptions import PermissionDenied


class BaseMultimediaContentRelatedModelAdmin(RelatedModelAdmin, BaseContentAdmin):
    list_filter = ('class_name', ) + BaseContentAdmin.list_filter
    inherit_actions = False
    related_field = 'multimediarelation'
    reverse_related_field = 'basecontent'


class MultimediaAddContentRelatedModelAdmin(BaseMultimediaContentRelatedModelAdmin):
    tool_name = 'addcontents'
    tool_label = _('associate contents')
    actions = ('associate_contents', )

    def queryset(self, request):
        multimedia = self.basecontent
        qs = BaseContent.objects.exclude(multimediarelation__multimedia=multimedia)
        user = request.user
        if not perms_api.can_manage_site(user) and\
           not perms_api.has_global_permission(user, 'edit'):
            owner_filter = Q(owners=request.user)
            if settings.ACQUIRE_SECTION_ROLES:
                owner_filter = owner_filter | Q(sections__owners=request.user)
            qs = qs.filter(owner_filter)
        return qs

    def associate_contents(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            perms_api.assert_has_permission_in_queryset(queryset, request.user, 'edit')
            if not self.has_change_permission(request):
                raise PermissionDenied(user=request.user, perm='edit')
            if request.POST.get('post'):
                multimedia = self.basecontent
                for content in queryset:
                    mr = MultimediaRelation(content=content, multimedia=multimedia)
                    mr.save(update_order=True)
                    obj_log = ugettext(u"%(content)s content associated to %(multimedia)s") % {
                        'content': content, 'multimedia': multimedia}
                    self.log_change(request, content, obj_log)
                msg_data = {'number': len(queryset),
                            'model_name': self.opts}
                msg = ugettext(u"Successfully associated %(number)d %(model_name)s.") % msg_data
                self.message_user(request, msg)
                return  # end action
            extra_context = {'title': ugettext(u'Are you sure you want to associate these contents?'),
                             'action_submit': 'associate_contents'}
            return self.confirm_action(request, queryset, extra_context)
    associate_contents.short_description = _(u"Associate contents")


class MultimediaRemoveContentRelatedModelAdmin(BaseMultimediaContentRelatedModelAdmin):
    actions = ('disassociate_contents', )
    tool_name = 'removecontents'
    tool_label = _('disassociate contents')

    def queryset(self, request):
        return self.basecontent.basecontent_set.all()

    def disassociate_contents(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            perms_api.assert_has_permission_in_queryset(queryset, request.user, 'edit')
            if not self.has_change_permission(request):
                raise PermissionDenied(user=request.user, perm='edit')
            if request.POST.get('post'):
                multimedia = self.basecontent
                for content in queryset:
                    MultimediaRelation.objects.get(content=content, multimedia=multimedia).delete()
                    obj_log = ugettext(u"%(content)s content associated to %(multimedia)s") % {
                        'content': content, 'multimedia': multimedia}
                    self.log_change(request, content, obj_log)
                msg_data = {'number': len(queryset),
                                'model_name': self.opts}
                msg = ugettext(u"Successfully disassociated %(number)d %(model_name)s.") % msg_data
                self.message_user(request, msg)
                return  # end action
            extra_context = {'title': ugettext('Are you sure you want disassociate this contents?'),
                             'action_submit': 'disassociate_contents'}
            return self.confirm_action(request, queryset, extra_context)
    disassociate_contents.short_description = _("Disassociate contents")


class BaseMultimediaAdmin(BaseAdmin, WorkflowBatchActionProvider):
    actions = BaseAdmin.actions + ['set_as_draft', 'set_as_pending', 'set_as_published']
    date_hierarchy = 'creation_date'
    list_filter = ('status', 'last_editor')
    list_display = ('__str__', 'status', 'last_editor')
    autocomplete_fields = {'tags':
            {'url': '/ajax/autocomplete/tags/multimedia/basemultimedia/',
             'multiple': True,
             'multipleSeparator': " ",
             'size': 100}, }

    def has_add_permission(self, request):
        """
            Overrides Django admin behaviour to add ownership based access control
        """
        return perms_api.can_manage_multimedia(request.user)

    def has_change_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        return self.has_add_permission(request)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({'is_multimedia': True})
        return super(BaseMultimediaAdmin, self).change_view(request, object_id,
                                                      extra_context)

    def save_model(self, request, obj, form, change):
        """
        Hack for saving object as pending when user is editor
        """
        obj.last_editor = request.user
        super(BaseMultimediaAdmin, self).save_model(request, obj, form, change)


class PendingBaseMultimediaAdmin(BaseMultimediaAdmin):
    list_display = ('__str__', 'admin_thumbnail', 'status', 'last_editor')
    change_list_template = 'admin/extra/change_list.html'

    def admin_thumbnail(self, item):
        instance = item.get_real_instance()
        if hasattr(instance, 'admin_thumbnail'):
            return instance.admin_thumbnail()
        else:
            return ''

    def changelist_view(self, request, extra_context=None):
        template_base = 'batchadmin/change_list.html'
        return super(PendingBaseMultimediaAdmin, self).changelist_view(request,
                                                             extra_context={'template_base': template_base,
                                                                            'admin_extra': True})

    admin_thumbnail.short_description = _('Thumbnail')
    admin_thumbnail.allow_tags = True


class PhotoAdmin(BaseMultimediaAdmin):

    change_list_template = ""
    list_display = ('__str__', 'admin_thumbnail', 'status', 'last_editor',
                    'contents')
    search_fields = ('name', 'original_filename')
    html_fields = ('caption', )

    def contents(self, obj):
        html = '<ul>'
        for content in obj.basecontent_set.all():
            html += u'<li><a href="' + content.get_admin_absolute_url() +\
                    u'">' + unicode(content) + u'</a></li>'
        for content in obj.basecity_set.all():
            html += u'<li><a href="' + content.get_admin_absolute_url() +\
                    u'">' + unicode(content) + u'</a></li>'
        for content in obj.province_set.all():
            html += u'<li><a href="' + content.get_admin_absolute_url() +\
                    u'">' + unicode(content) + u'</a></li>'
        html += '</ul>'
        return mark_safe(html)
    contents.allow_tags = True

    def queryset(self, request):
        qs = super(PhotoAdmin, self).queryset(request)
        class_name = request.GET.get('class_name', None)
        if class_name:
            get = request.GET.copy()
            qs = qs.filter(basecontent__class_name=class_name)
            get.pop('class_name')
            request.CLASS_NAME = class_name
            request.GET = get
        return qs

    def changelist_view(self, request, extra_context=None):
        from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
        try:
            cl = ChangeList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self.list_editable, self)
            cl.formset = None
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': ugettext('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        class_name = getattr(request, 'CLASS_NAME', None)
        cl.has_filters = True
        class_names = [{'name': ugettext('All'), 'url': cl.get_query_string(remove='class_name')}]
        for i in BaseContent.objects.order_by('class_name').values('class_name').distinct():
            class_names.append({'name': i['class_name'],
                                'url': cl.get_query_string(new_params={'class_name': i['class_name']})})
        if class_name:
            cl.params.update({'class_name': class_name})

        context = {
            'cl': cl,
            'class_names': class_names,
        }
        context.update(extra_context or {})
        return super(PhotoAdmin, self).changelist_view(request, context)


class VideoChecker(object):
    form = VideoCheckerModelForm


class VideoAdmin(VideoChecker, BaseMultimediaAdmin):
    search_fields = ('name', 'original_filename')
    list_display = ('__str__', 'status', 'last_editor')


class PanoramicViewAdmin(BaseMultimediaAdmin):
    search_fields = ('name', 'original_filename')
    list_display = ('__str__', 'status', 'last_editor')


class Image3DAdmin(BaseMultimediaAdmin):
    search_fields = ('name', 'original_filename')
    list_display = ('__str__', 'status', 'last_editor')

    def get_form(self, request, obj=None):
        form = super(Image3DAdmin, self).get_form(request, obj)

        def clean(self):
            super(form, self).clean()
            file_cleaned_data = self.cleaned_data.get('file', None)
            old_file = obj and obj.file
            if not old_file and not file_cleaned_data:
                global_errors = self.errors.get('__all__', ErrorList([]))
                global_errors.extend(ErrorList([ugettext(u'Please specify at least a video file ')]))
                self._errors['__all__'] = ErrorList(global_errors)
            elif file_cleaned_data:
                extension = file_cleaned_data.name.split('.')[-1].lower()
                if extension not in ('swf', 'swf'):
                    file_errors = self.errors.get('file', ErrorList([]))
                    file_errors.extend(ErrorList([ugettext(u'This file must be in swf format')]))
                    self._errors['file'] = ErrorList(file_errors)
            return self.cleaned_data
        form.clean = clean
        return form


class AudioChecker(object):
    form = AudioCheckerModelForm


class AudioAdmin(AudioChecker, BaseMultimediaAdmin):
    search_fields = ('name', 'original_filename')
    list_display = ('__str__', 'status', 'last_editor')


class RelatedBaseMultimediaAdmin(OrderableRelatedModelAdmin):
    sortablefield = 'order'
    search_fields = ('name', 'original_filename')
    list_display = ('__str__', 'status', 'last_editor')
    related_field = 'basecontent'
    manage_contents = True

    def custom_relate_content(self, request, obj, form, change):
        if not change:
            MultimediaRelation.objects.create(content=self.basecontent,
                multimedia=obj.basemultimedia_ptr)

    def get_relation_obj(self, through_model, obj):
        return through_model.objects.get(
            content=self.basecontent, multimedia=obj,
        )


class RelatedPhotoAdmin(RelatedBaseMultimediaAdmin):
    tool_name = 'photos'
    tool_label = _('photos')
    list_display = ('__str__', 'admin_thumbnail', 'status', 'last_editor', )


class RelatedVideoAdmin(VideoChecker, RelatedBaseMultimediaAdmin):
    tool_name = 'videos'
    tool_label = _('videos')


class RelatedPanoramicViewAdmin(RelatedBaseMultimediaAdmin):
    tool_name = 'panoramicviews'
    tool_label = _('panoramic views')


class RelatedImage3DAdmin(RelatedBaseMultimediaAdmin):
    tool_name = 'images3d'
    tool_label = _('3d images')


class RelatedFileAdmin(RelatedBaseMultimediaAdmin):
    tool_name = 'files'
    tool_label = _('files')


class RelatedAudioAdmin(AudioChecker, RelatedBaseMultimediaAdmin):
    tool_name = 'audios'
    tool_label = _('audio files')


def register(site):
    register_related_multimedia(site, BaseContent)


def register_related_multimedia(site, related_to):
    site.register_related(Photo, RelatedPhotoAdmin, related_to=related_to)
    site.register_related(Video, RelatedVideoAdmin, related_to=related_to)
    # PanoramicView and Image3D are not fully implemented, so we hide them
    #site.register_related(PanoramicView, RelatedPanoramicViewAdmin, related_to=related_to)
    #site.register_related(Image3D, RelatedImage3DAdmin, related_to=related_to)
    site.register_related(File, RelatedFileAdmin, related_to=related_to)
    site.register_related(Audio, RelatedAudioAdmin, related_to=related_to)

    site.register_related(BaseContent, MultimediaAddContentRelatedModelAdmin, related_to=BaseMultimedia)
    site.register_related(BaseContent, MultimediaRemoveContentRelatedModelAdmin, related_to=BaseMultimedia)
