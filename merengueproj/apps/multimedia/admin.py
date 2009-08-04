from django.contrib.admin.options import IncorrectLookupParameters
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group

from base.admin import BaseContentAdmin, BaseAdmin, VideoChecker,\
                       WorkflowBatchActionProvider, BaseContentRelatedModelAdmin
from base.models import BaseContent, MultimediaRelation
from batchadmin.util import get_changelist
from multimedia.models import Photo, Video, PanoramicView, Image3D, Audio


class BaseMultimediaRelatedBaseContentModelAdmin(BaseContentAdmin, BaseContentRelatedModelAdmin):

    list_filter = ('class_name', ) + BaseContentAdmin.list_filter


class BaseMultimediaRelatedAddContentModelAdmin(BaseMultimediaRelatedBaseContentModelAdmin):

    batch_actions = ['associate_contents']

    def queryset(self, request):
        multimedia = self.admin_site.basecontent
        return BaseContent.objects.exclude(multimediarelation__multimedia=multimedia)

    def associate_contents(self, request, changelist):
        objects_id = request.POST.getlist('selected')
        if objects_id:
            if request.POST.get('post'):
                changelist = get_changelist(request, self.model, self)
                multimedia = self.admin_site.basecontent
                basecontents = BaseContent.objects.filter(id__in=objects_id)
                for basecontent in basecontents:
                    mr = MultimediaRelation(content=basecontent, multimedia=multimedia)
                    mr.save(update_order=True)
                return self.change_state(request, changelist, state='published')
            extra_context = {'title': _('Are you sure you want associate this contents?'),
                             'action_submit': 'associate_contents'}
            return self.confirm_action(request, objects_id, extra_context)
    associate_contents.short_description = _("Associate contents")


class BaseMultimediaRelatedRemoveContentModelAdmin(BaseMultimediaRelatedBaseContentModelAdmin):
    batch_actions = ['disassociate_contents']

    def queryset(self, request):
        return self.admin_site.basecontent.basecontent_set.all()

    def disassociate_contents(self, request, changelist):
        objects_id = request.POST.getlist('selected')
        if objects_id:
            if request.POST.get('post'):
                changelist = get_changelist(request, self.model, self)
                multimedia = self.admin_site.basecontent
                basecontents = BaseContent.objects.filter(id__in=objects_id)
                for basecontent in basecontents:
                    MultimediaRelation.objects.get(content=basecontent, multimedia=multimedia).delete()
                return self.change_state(request, changelist, state='published')
            extra_context = {'title': _('Are you sure you want disassociate this contents?'),
                             'action_submit': 'disassociate_contents'}
            return self.confirm_action(request, objects_id, extra_context)
    disassociate_contents.short_description = _("Disassociate contents")


class BaseMultimediaAdmin(BaseAdmin, WorkflowBatchActionProvider):
    batch_actions = BaseAdmin.batch_actions + ['set_as_draft', 'set_as_pending',
                                               'set_as_published', ]
    batch_actions_perms = {'set_as_draft': 'base.can_draft',
                           'set_as_pending': 'base.can_pending',
                           'set_as_published': 'base.can_published',
                          }
    date_hierarchy = 'creation_date'
    list_filter = ('status', 'last_editor')
    list_display = ('__str__', 'status', 'last_editor')
    autocomplete_fields = {'tags':
            {'url': '/ajax/autocomplete/tags/multimedia/basemultimedia/',
             'multiple': True,
             'multipleSeparator': " ",
             'size': 100}, }

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
        if not change:
            try:
                editors_group = Group.objects.get(name='editores')
            except Group.DoesNotExist:
                editors_group = None
            if editors_group and editors_group in request.user.groups.all():
                obj.status = 'pending'
        super(BaseMultimediaAdmin, self).save_model(request, obj, form, change)


class PendingBaseMultimediaAdmin(BaseMultimediaAdmin):
    list_display = ('__str__', 'admin_thumbnail', 'status', 'last_editor')
    change_list_template = 'admin/extra/change_list.html'

    def admin_thumbnail(self, item):
        instance = item._get_real_instance()
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
            request.GET=get
        return qs

    def changelist_view(self, request, extra_context=None):
        from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
        try:
            cl = ChangeList(request, self.model, self.list_display, self.list_display_links, self.list_filter,
                self.date_hierarchy, self.search_fields, self.list_select_related, self.list_per_page, self)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        class_name = getattr(request, 'CLASS_NAME', None)
        cl.has_filters=True
        class_names=[{'name': _('All'), 'url': cl.get_query_string(remove='class_name')}]
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
            url_cleaned_data = self.cleaned_data.get('external_url', None)
            old_file = obj and obj.file
            if not old_file and not file_cleaned_data:
                global_errors = self.errors.get('__all__', ErrorList([]))
                global_errors.extend(ErrorList([_(u'Please specify at least a video file ')]))
                self._errors['__all__'] = ErrorList(global_errors)
            elif file_cleaned_data:
                extension = file_cleaned_data.name.split('.')[-1].lower()
                if extension not in ('swf', 'swf'):
                    file_errors = self.errors.get('file', ErrorList([]))
                    file_errors.extend(ErrorList([_(u'This file must be in swf format')]))
                    self._errors['file'] = ErrorList(file_errors)
            return self.cleaned_data
        form.clean = clean
        return form


class AudioAdmin(BaseMultimediaAdmin):
    search_fields = ('name', 'original_filename')
    list_display = ('__str__', 'status', 'last_editor')


def register(site):
    site.register(Photo, PhotoAdmin)
    site.register(Video, VideoAdmin)
    site.register(PanoramicView, PanoramicViewAdmin)
    site.register(Image3D, Image3DAdmin)
    site.register(Audio, AudioAdmin)
