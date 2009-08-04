from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.contenttypes.models import ContentType
from django.forms.models import save_instance
from django.forms.util import ValidationError
from django.forms.widgets import HiddenInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from base.models import BaseContent
from base.admin import (BaseAdmin, BaseContentRelatedModelAdmin,
                        WorkflowBatchActionProvider)
from batchadmin.util import get_changelist
from multimedia.models import Photo
from section.models import (Menu, Section, AppSection, Carousel,
                            BaseLink, AbsoluteLink, DocumentLink, Document)
from section.widgets import ModifiedRelatedFieldWidgetWrapper, SearchFormOptionsWidget


class MenuAdmin(BaseAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_es', )}


class BaseSectionAdmin(BaseAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_es', )}

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseSectionAdmin, self).get_form(request, obj, **kwargs)
        if 'main_document' in form.base_fields.keys():
            qs = form.base_fields['main_document'].queryset
            if not obj:
                qs = qs.model.objects.get_empty_query_set()
            else:
                qs = qs.filter(related_section=obj)
            # Como Document no esta registrado en el admin site, no tiene
            # sentido mostrar este campo si no tiene opciones ya que no
            # se pueden crear nuevos documentos desde aqui
            if qs.count():
                form.base_fields['main_document'].queryset = qs
            else:
                form.base_fields.pop('main_document')
        return form


class AbsoluteLinkAdmin(BaseAdmin):
    list_display = ('url', )


class DocumentLinkAdmin(BaseAdmin):
    list_display = ('document', )


class SectionAdmin(BaseSectionAdmin):
    list_display = ('name', 'slug')


class BaseSectionRelatedCustomStyleModelAdmin(BaseContentRelatedModelAdmin):
    fieldsets = (
        (_('CSS Colors'), {'fields': ('color_1', 'color_2', 'color_3', 'menu_link_color')}),
        (_('Header images'), {'fields': ('content_head_background', 'menu_head_background')}),
        (_('Searcher images'), {'fields': ('searcher_left_arrow', 'searcher_right_arrow',
                                           'searcher_tab_image', 'searcher_last_tab_image',
                                           'search_results_item_background')}),
        )

    def changelist_view(self, request, extra_context=None):
        if not self.admin_site.basecontent.customstyle:
            return self.add_view(request, extra_context=extra_context)
        else:
            object_id = "%s" % self.admin_site.basecontent.customstyle.id
            return self.change_view(request, object_id=object_id, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        if object_id == 'delete':
            object_id = "%s" % self.admin_site.basecontent.customstyle.id
            return self.delete_view(request, object_id, extra_context)
        else:
            return super(BaseSectionRelatedCustomStyleModelAdmin, self).change_view(request, object_id, extra_context)

    def queryset(self, request):
        return self.admin_site.basecontent.customstyle

    def save_model(self, request, obj, form, change):
        super(BaseSectionRelatedCustomStyleModelAdmin, self).save_model(request, obj, form, change)
        if not change:
            self.admin_site.basecontent.customstyle = obj
            self.admin_site.basecontent.save()

    def has_delete_permission(self, request, obj=None):
        return False

    def response_add(self, request, obj, post_url_continue='../%s/'):
        post_url_continue='%s/'
        return super(BaseSectionRelatedCustomStyleModelAdmin, self).response_add(request, obj, post_url_continue)


class ReadOnlySlugWidget(HiddenInput):

    def render(self, name, value, attrs=None):
        output = super(ReadOnlySlugWidget, self).render(name, value, attrs)
        return mark_safe(output + value)


class BaseDocumentModelAdmin(object):

    def post_save_model(self, request, obj, form, change):
        app_section = obj.related_section
        try:
            if app_section:
                app_section.document_set.exclude(pk=obj.pk).get(slug=obj.slug)
                obj.slug = "%s-%s" %(obj.slug, obj.id)
                obj.save()
            else:
                obj.__class__.objects.get(slug=obj.slug)
                obj.slug = "%s-%s" %(obj.slug, obj.id)
                obj.save()
        except Document.DoesNotExist:
            pass


class BaseSectionRelatedDocumentModelAdmin(BaseContentRelatedModelAdmin, WorkflowBatchActionProvider, BaseDocumentModelAdmin):
    selected = 'documents'
    change_list_template = "admin/section/document/change_list.html"
    list_display = ('name', 'slug', 'status', )
    list_filter = ('status', )
    html_fields = ('body', )
    prepopulated_fields = {'slug': ('name_es', )}
    filter_horizontal = ('videos', )

    batch_actions = BaseAdmin.batch_actions + ['set_as_draft',
                                               'set_as_published']
    batch_actions_perms = {'set_as_draft': 'base.can_draft',
                           'set_as_published': 'base.can_published',
                          }

    def queryset(self, request):
        return self.admin_site.basecontent.document_set.all()

    def save_model(self, request, obj, form, change):
        obj.related_section = self.admin_site.basecontent
        super(BaseSectionRelatedDocumentModelAdmin, self).save_model(
                                                request, obj, form, change)
        self.post_save_model(request, obj, form, change)

    def has_change_permission_to_any(self, request):
        return super(BaseSectionRelatedDocumentModelAdmin, self).has_change_permission(request, None)

    def has_delete_permission(self, request, obj=None):
        if obj:
            return not obj.permanent
        return super(BaseSectionRelatedDocumentModelAdmin, self).has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseSectionRelatedDocumentModelAdmin, self).get_form(
                                                    request, obj, **kwargs)
        if 'related_section' in form.base_fields.keys():
            form.base_fields.pop('related_section')

        form = super(BaseSectionRelatedDocumentModelAdmin, self).get_form(request, obj, **kwargs)
        if 'status' in form.base_fields.keys():
            user = request.user
            options = self._get_status_options(user, obj)
            if options:
                form.base_fields['status'].choices = options
            else:
                form.base_fields.pop('status')

        if obj and obj.permanent and 'slug' in form.base_fields.keys():
            slugfield = form.base_fields['slug']
            slugfield.widget = ReadOnlySlugWidget(slugfield.widget.attrs)

        return form

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'search_form':
            from searchform.registry import search_form_registry
            db_field._choices = search_form_registry.get_choices()

        formfield = super(BaseSectionRelatedDocumentModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'search_form_filters':
            formfield.widget = SearchFormOptionsWidget()

        return formfield

    def __call__(self, request, url):
        self.selected = 'main_menu'
        self.selected_menu = self.admin_site.basecontent.main_menu
        return super(BaseSectionRelatedDocumentModelAdmin, self).__call__(request, url)


class BaseLinkInline(admin.TabularInline):

    def get_fieldsets(self, request, obj=None):
        if self.declared_fieldsets:
            return self.declared_fieldsets
        formset = self.get_formset(request)
        if not formset:
            return []
        else:
            form = formset.form
            return [(None, {'fields': form.base_fields.keys()})]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(BaseLinkInline, self).get_formset(request, obj=None, **kwargs)
        if obj:
            try:
                if not isinstance(obj.baselink.real_instance, self.model):
                    return None
            except BaseLink.DoesNotExist:
                pass

        def save_new(formset_self, form, commit=True):
            fk_attname = formset_self.fk.get_attname()
            kwargs = {fk_attname: formset_self.instance.pk}
            new_obj = formset_self.model(**kwargs)
            if fk_attname == formset_self._pk_field.attname:
                exclude = [formset_self._pk_field.name]
            else:
                exclude = []
            if 'baselink_ptr' in form.cleaned_data and not form.cleaned_data['baselink_ptr']:
                del(form.cleaned_data['baselink_ptr'])
            return save_instance(form, new_obj, exclude=exclude, commit=commit)

        def clean(formset_self):
            data=formset_self.data
            if data.get('documentlink-0-document', None) and data.get('absolutelink-0-url', None):
                raise ValidationError(_('Sorry you can not select an Absolute Link and a Document Link simultaneously for this menu. Fulfill just one.'))
        formset.save_new=save_new
        formset.clean=clean
        return formset


class AbsoluteLinkInline(BaseLinkInline):
    model = AbsoluteLink
    max_num = 1
    verbose_name = _('Menu Absolute Link')
    verbose_name_plural = _('Menu Absolute Links')

    def _media(self):
        from django import forms

        js = ['%sjs/tiny_mce_internal_links/no_tiny_mce_internal_links.js' % settings.MEDIA_URL]
        if self.prepopulated_fields:
            js.append('%sjs/urlify.js' % settings.ADMIN_MEDIA_PREFIX)
        if self.filter_vertical or self.filter_horizontal:
            js.extend(['%sjs/SelectBox.js' % settings.ADMIN_MEDIA_PREFIX,
                       '%sjs/SelectFilter2.js' % settings.ADMIN_MEDIA_PREFIX])
        return forms.Media(js=js)
    media = property(_media)

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(AbsoluteLinkInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'url':

            def clean(value):
                return value
            field.clean=clean
        return field


class DocumentLinkInline(BaseLinkInline):
    model = DocumentLink
    max_num = 1
    verbose_name = _('Menu Document Link')
    verbose_name_plural = _('Menu Document Links')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(DocumentLinkInline, self).formfield_for_dbfield(db_field, **kwargs)
        if formfield and isinstance(formfield.widget, RelatedFieldWidgetWrapper):
            formfield.widget = ModifiedRelatedFieldWidgetWrapper(
                    formfield.widget.widget,
                    formfield.widget.rel,
                    formfield.widget.admin_site)
        return formfield

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(DocumentLinkInline, self).get_formset(request, obj, **kwargs)
        if not formset:
            return formset
        form=formset.form
        if 'document' in form.base_fields.keys():
            qs = form.base_fields['document'].queryset
            qs = qs.filter(related_section=self.admin_site.basecontent)
            form.base_fields['document'].queryset = qs
        return formset


class BaseSectionRelatedMenuModelAdmin(BaseContentRelatedModelAdmin):
    selected = 'main_menu'
    change_list_template = "admin/section/menu/change_list.html"
    list_display = ('level', 'name', 'slug', 'display_move_to', )
    list_display_links = ('name', )
    prepopulated_fields = {'slug': ('name_es', )}
    ordering=('lft', )
    batch_actions = []
    actions_on_top = False
    actions_on_bottom = False
    inlines = [AbsoluteLinkInline, DocumentLinkInline]

    def __init__(self, *args, **kwargs):
        super(BaseSectionRelatedMenuModelAdmin, self).__init__(*args, **kwargs)
        self.old_inline_instances = [instance for instance in self.inline_instances]
        if 'batchadmin_checkbox' in self.list_display:
            self.list_display.remove('batchadmin_checkbox')

    def __call__(self, request, url):
        self.selected = 'main_menu'
        self.selected_menu = self.admin_site.basecontent.main_menu
        if url and url.startswith('interest'):
            self.selected ='interest_menu'
            self.selected_menu = self.admin_site.basecontent.interest_menu
            url = url[9:] or None
        elif url and url.startswith('secondary'):
            self.selected ='secondary_menu'
            self.selected_menu = self.admin_site.basecontent.secondary_menu
            url = url[10:] or None
        return super(BaseSectionRelatedMenuModelAdmin, self).__call__(request, url)

    def display_move_to(self, menu):
        hidden = u'<input type="hidden" class="thisMenu" name="next" value="%s" />' % menu.id
        init_move = u'<a href="#" class="initMoveMenu" title="%(title)s">%(title)s</a>' % {'title': ugettext(u'Move this menu')}
        cancel_move = u'<a href="#" class="cancelMoveMenu hide" title="%(title)s">%(title)s</a>' % {'title': ugettext(u'Cancel move')}
        options = (
            u'<li><a href="#" class="insertPrev" title="%(title)s">%(title)s</a></li>' % {'title': ugettext(u'Before')},
            u'<li><a href="#" class="insertNext" title="%(title)s">%(title)s</a></li>' % {'title': ugettext(u'After')},
            u'<li><a href="#" class="insertChild" title="%(title)s">%(title)s</a></li>' % {'title': ugettext(u'Child')},
            )
        options = u'<ul class="insertOptions hide">' + u''.join(options) + u'</ul>'
        return mark_safe('%s%s%s%s' % (hidden, init_move, cancel_move, options))
    display_move_to.allow_tags=True

    def queryset(self, request):
        if not self.selected_menu:
            return Menu.tree.get_empty_query_set()
        else:
            return Menu.tree.filter(tree_id=self.selected_menu.tree_id, level__gt=0)

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseSectionRelatedMenuModelAdmin, self).get_form(
                                                    request, obj, **kwargs)
        if 'parent' in form.base_fields.keys():
            qs = form.base_fields['parent'].queryset
            qs = qs.filter(tree_id=self.selected_menu.tree_id, level__gt=0)
            form.base_fields['parent'].queryset = qs
        return form

    def get_formsets(self, request, obj=None):
        self.inline_instances = []
        res = []
        for inline in self.old_inline_instances:
            formset = inline.get_formset(request, obj)
            if formset:
                self.inline_instances.append(inline)
                res.append(formset)
        return res

    def save_model(self, request, obj, form, change):
        if not obj.parent:
            obj.parent = self.selected_menu
        super(BaseSectionRelatedMenuModelAdmin, self).save_model(
                                                request, obj, form, change)

    def move_menus(self, request):
        source_id = request.GET.pop('source', None)
        target_id = request.GET.pop('target', None)
        movement = request.GET.pop('movement', None)
        if not source_id and not target_id and not movement:
            return

        if source_id and target_id and movement:
            query = self.queryset(request)
            try:
                source_menu = query.get(id=source_id[0])
                target_menu = query.get(id=target_id[0])
                source_menu.move_to(target_menu, movement[0])
                return source_id[0]
            except:
                pass

    def changelist_view(self, request, extra_context={}):
        source = self.move_menus(request)
        media = self.media
        media.add_js([settings.MEDIA_URL + "js/CollapsableMenuTree.js"])
        extra_context.update({'media': media.render(),
                              'moved_source': source})
        return super(BaseSectionRelatedMenuModelAdmin, self).changelist_view(
                                                        request, extra_context)


class AppSectionAdmin(BaseSectionAdmin):
    list_display = ('name', 'slug', 'app_name')
    prepopulated_fields = {'slug': ('name_es', )}
    batch_actions = []
    actions_on_top = False
    actions_on_bottom = False

    def __init__(self, *args, **kwargs):
        super(AppSectionAdmin, self).__init__(*args, **kwargs)
        self.old_prepopulated_fields = self.prepopulated_fields
        if 'batchadmin_checkbox' in self.list_display:
            self.list_display.remove('batchadmin_checkbox')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super(AppSectionAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            if 'slug' in form.base_fields.keys():
                form.base_fields.pop('slug')
            if 'slug' in self.prepopulated_fields.keys():
                self.prepopulated_fields.pop('slug')
        else:
            self.prepopulated_fields = self.old_prepopulated_fields
        return form


class CarouselAdmin(BaseAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name', )}
    exclude = ('photos_extra', )

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(BaseAdmin, self).formfield_for_dbfield(db_field,
                                                             **kwargs)

        if db_field.name == 'class_name':
            base_contents = BaseContent.objects.all().values('class_name')\
                                                     .distinct('class_name')
            base_contents_class_name = [v['class_name'] for v in base_contents\
                                        if v['class_name']]
            field.queryset = ContentType.objects.filter(
                                    model__in=base_contents_class_name)
        return field

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({'is_carousel': True})
        return super(CarouselAdmin, self).change_view(request, object_id,
                                                      extra_context)


class CarouselRelatedPhotoModelAdmin(BaseContentRelatedModelAdmin):
    list_display = ('__str__', 'admin_thumbnail', 'status')
    html_fields = ('caption', )
    search_fields = ('name', 'original_filename')
    selected = 'photos'
    change_list_template = None

    def _update_extra_context(self, extra_context=None):
        extra_context = super(CarouselRelatedPhotoModelAdmin, self)._update_extra_context(extra_context)
        extra_context['inside_basecontent'] = False
        extra_context['inside_carousel_section'] = True
        return extra_context

    def save_model(self, request, obj, form, change):
        super(CarouselRelatedPhotoModelAdmin, self).save_model(request, obj, form, change)
        self.admin_site.basecontent.photos_extra.add(obj)


class CarouselRelatedAddPhotoModelAdmin(CarouselRelatedPhotoModelAdmin):
    batch_actions = ['select_photo']

    def select_photo(self, request, changelist):
        objects_id = request.POST.getlist('selected')

        if objects_id:
            if request.POST.get('post'):
                changelist = get_changelist(request, self.model, self)
                photos_selected = Photo.objects.filter(id__in=objects_id)
                object = self.admin_site.basecontent
                for photo_selected in photos_selected:
                    object.photos_extra.add(photo_selected)
                return
            extra_context = {'title':
                                _('Are you sure you want select this photos?'),
                             'action_submit': 'select_photo'}
            return self.confirm_action(request, objects_id, extra_context)
    select_photo.short_description = _("Select photo")


class CarouselRelatedRemovePhotoModelAdmin(CarouselRelatedPhotoModelAdmin, WorkflowBatchActionProvider):
    batch_actions = ['deselect_photo', 'set_as_draft', 'set_as_pending', 'set_as_published']
    batch_actions_perms = {
        'set_as_draft': 'base.can_draft',
        'set_as_pending': 'base.can_pending',
        'set_as_published': 'base.can_published',
    }

    def deselect_photo(self, request, changelist):
        objects_id = request.POST.getlist('selected')
        if objects_id:
            if request.POST.get('post'):
                changelist = get_changelist(request, self.model, self)
                photos_deselected = Photo.objects.filter(id__in=objects_id)
                object = self.admin_site.basecontent
                for photo_deselected in photos_deselected:
                    object.photos_extra.remove(photo_deselected)
                return
            extra_context = {'title':
                                _('Are you sure you want deselect this photos?'),
                             'action_submit': 'deselect_photo'}
            return self.confirm_action(request, objects_id, extra_context)
    deselect_photo.short_description = _("Deselect photo")

    def queryset(self, request):
        return Photo.objects.filter(carousel=self.admin_site.basecontent)


class DocumentAdmin(BaseAdmin, WorkflowBatchActionProvider, BaseDocumentModelAdmin):
    change_form_template = 'admin/section/document/change_form.html'

    list_display = ('name', 'slug', 'status', )
    list_filter = ('status', )
    html_fields = ('body', )
    filter_horizontal=('videos', )
    prepopulated_fields = {'slug': ('name_es', )}
    batch_actions = BaseAdmin.batch_actions + ['set_as_published', 'set_as_draft']

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'search_form':
            from searchform.registry import search_form_registry
            db_field._choices = search_form_registry.get_choices()

        formfield = super(DocumentAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'search_form_filters':
            formfield.widget = SearchFormOptionsWidget()
        if db_field.name == 'name_en':
            formfield.required = True

        return formfield


class NoSectionDocumentAdmin(DocumentAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super(NoSectionDocumentAdmin, self).get_form(request, obj, **kwargs)
        if 'related_section' in form.base_fields.keys():
            form.base_fields.pop('related_section')
        return form

    def save_model(self, request, obj, form, change):
        app_section = None
        try:
            app_name = settings.APP_SECTION_MAP[obj._meta.module_name]
            app_section = AppSection.objects.get(slug=app_name)
            obj.related_section = app_section
        except AppSection.DoesNotExist:
            pass
        obj.save()
        self.post_save_model(request, obj, form, change)


def register(site):
    site.register(Section, SectionAdmin)
    site.register(AppSection, AppSectionAdmin)
    site.register(Carousel, CarouselAdmin)
