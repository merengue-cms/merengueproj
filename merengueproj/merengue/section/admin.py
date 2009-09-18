from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.forms.models import save_instance
from django.forms.util import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from merengue.base.models import BaseContent
from merengue.base.admin import BaseAdmin, RelatedModelAdmin
from merengue.base.admin import set_field_read_only
from merengue.multimedia.models import Photo
from merengue.section.models import (Menu, Section, AppSection, Carousel,
                            BaseLink, AbsoluteLink, ContentLink, Document,
                            DocumentSection, CustomStyle)
from merengue.section.widgets import SearchFormOptionsWidget


class MenuAdmin(BaseAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_es', )}


class BaseSectionAdmin(BaseAdmin):
    list_display = ('name', 'slug', )
    html_fields = ('description', )
    prepopulated_fields = {'slug': ('name_es', )}

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseSectionAdmin, self).get_form(request, obj, **kwargs)
        if 'main_content' in form.base_fields.keys():
            qs = form.base_fields['main_content'].queryset
            if not obj:
                qs = qs.model.objects.get_empty_query_set()
            else:
                qs = qs.filter(basesection=obj)
            # Como Document no esta registrado en el admin site, no tiene
            # sentido mostrar este campo si no tiene opciones ya que no
            # se pueden crear nuevos documentos desde aqui
            if qs.count():
                form.base_fields['main_content'].queryset = qs
            else:
                form.base_fields.pop('main_content')
        return form


class AbsoluteLinkAdmin(BaseAdmin):
    list_display = ('url', )


class ContentLinkAdmin(BaseAdmin):
    list_display = ('content', )


class SectionAdmin(BaseSectionAdmin):
    list_display = ('name', 'slug')

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['change_form_section'] = True
        return super(SectionAdmin, self).render_change_form(request, context, add, change, form_url, obj)


class SectionContentAdmin(RelatedModelAdmin):
    related_field = 'basesection'


class CustomStyleRelatedModelAdmin(RelatedModelAdmin):
    fieldsets = (
        (_('CSS Colors'), {'fields': ('color_1', 'color_2', 'color_3', 'menu_link_color')}),
        (_('Header images'), {'fields': ('content_head_background', 'menu_head_background')}),
        (_('Searcher images'), {'fields': ('searcher_left_arrow', 'searcher_right_arrow',
                                           'searcher_tab_image', 'searcher_last_tab_image',
                                           'search_results_item_background')}),
        )
    tool_name = 'style'
    tool_label = _('custom style')
    related_field = 'basesection'
    one_to_one = True

    def has_delete_permission(self, request, obj=None):
        return False


class DocumentAdmin(SectionContentAdmin):
    list_display = ('name', 'slug', 'status', )
    list_filter = ('status', )
    html_fields = ('description', 'body', )
    filter_horizontal=('videos', )
    prepopulated_fields = {'slug': ('name_es', )}
    actions = BaseAdmin.actions + ['set_as_published', 'set_as_draft']


class DocumentRelatedModelAdmin(DocumentAdmin):
    tool_name = 'documents'
    tool_label = _('documents')

    def get_form(self, request, obj=None, **kwargs):
        form = super(DocumentRelatedModelAdmin, self).get_form(request, obj, **kwargs)
        if obj and obj.permanent and 'slug' in form.base_fields.keys():
            set_field_read_only(form.base_fields['slug'], 'slug', obj)
        return form

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'search_form':
            from searchform.registry import search_form_registry
            db_field._choices = search_form_registry.get_choices()

        formfield = super(DocumentRelatedModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'search_form_filters':
            formfield.widget = SearchFormOptionsWidget()

        return formfield


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
            if data.get('contentlink-0-content', None) and data.get('absolutelink-0-url', None):
                raise ValidationError(_('Sorry you can not select an Absolute Link and a Content Link simultaneously for this menu. Fulfill just one.'))
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


class ContentLinkInline(BaseLinkInline):
    model = ContentLink
    max_num = 1
    verbose_name = _('Menu Content Link')
    verbose_name_plural = _('Menu Content Links')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(ContentLinkInline, self).get_formset(request, obj, **kwargs)
        if not formset:
            return formset
        form = formset.form
        if 'content' in form.base_fields.keys():
            qs = form.base_fields['content'].queryset
            qs = qs.filter(basesection=self.admin_model.basecontent)
            form.base_fields['content'].queryset = qs
        return formset


class BaseSectionMenuRelatedAdmin(RelatedModelAdmin):
    change_list_template = "admin/section/menu/change_list.html"
    list_display = ('level', 'display_move_to', 'name', 'slug', )
    list_display_links = ('name', )
    prepopulated_fields = {'slug': ('name_es', )}
    ordering=('lft', )
    actions = []
    inherit_actions = False
    inlines = [AbsoluteLinkInline, ContentLinkInline]

    def __init__(self, *args, **kwargs):
        super(BaseSectionMenuRelatedAdmin, self).__init__(*args, **kwargs)
        self.old_inline_instances = [instance for instance in self.inline_instances]

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

    def get_menu(self, request, basecontent=None):
        return super(BaseSectionMenuRelatedAdmin, self).queryset(request, basecontent).get()

    def get_section_docs(self, request):
        section = getattr(self.get_menu(request), self.related_field)
        return section.content_set.all()

    def queryset(self, request, basecontent=None):
        menu = self.get_menu(request, basecontent)
        if not menu:
            return Menu.tree.get_empty_query_set()
        else:
            return Menu.tree.filter(tree_id=menu.tree_id, level__gt=0)

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseSectionMenuRelatedAdmin, self).get_form(
                                                    request, obj, **kwargs)
        if 'parent' in form.base_fields.keys():
            qs = form.base_fields['parent'].queryset
            qs = qs.filter(tree_id=self.get_menu(request).tree_id, level__gt=0)
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
            obj.parent = self.get_menu(request)
        super(BaseSectionMenuRelatedAdmin, self).save_model(
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
        media.add_js([settings.MEDIA_URL + "merengue/js/jquery-1.2.6.min.js"])
        media.add_js([settings.MEDIA_URL + "merengue/js/jquery-ui-1.5.3.custom.min.js"])
        media.add_js([settings.MEDIA_URL + "merengue/js/section/CollapsableMenuTree.js"])
        media.add_js([settings.MEDIA_URL + "merengue/js/section/OrderableMenuTree.js"])
        extra_context.update({'media': media.render(),
                              'moved_source': source})
        return super(BaseSectionMenuRelatedAdmin, self).changelist_view(
                                                        request, extra_context)


class MainMenuRelatedAdmin(BaseSectionMenuRelatedAdmin):
    tool_name = 'mainmenu'
    tool_label = _('main menu')
    related_field = 'main_menu_section'


class SecondaryMenuRelatedAdmin(BaseSectionMenuRelatedAdmin):
    tool_name = 'secondarymenu'
    tool_label = _('secondary menu')
    related_field = 'secondary_menu_section'


class AppSectionAdmin(BaseSectionAdmin):
    list_display = ('name', 'slug', 'app_name')
    prepopulated_fields = {'slug': ('name_es', )}
    actions = []
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
    exclude = ('photo_list', )

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


class CarouselPhotoRelatedModelAdmin(RelatedModelAdmin):
    """ Add new photos to carousel or remove existing ones """
    tool_name = 'photos'
    tool_label = _('photos')
    related_field = 'carousel'
    list_display = ('__str__', 'admin_thumbnail', 'status')
    html_fields = ('caption', )
    search_fields = ('name', 'original_filename')
    selected = 'photos'
    change_list_template = None
    actions = ['deselect_photo', ]

    def deselect_photo(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            if request.POST.get('post'):
                basecontent = self.basecontent
                for deselected_photo in queryset:
                    basecontent.photo_list.remove(deselected_photo)
                return
            extra_context = {'title': _(u'Are you sure you want to deselect these photos from carousel?'),
                             'action_submit': 'deselect_photo'}
            return self.confirm_action(request, queryset, extra_context)
    deselect_photo.short_description = _("Deselect photo")


class CarouselRelatedChoosePhotoModelAdmin(CarouselPhotoRelatedModelAdmin):
    """ Choose existing photos for a carousel """
    tool_name = 'choosephotos'
    tool_label = _('choose photos')
    actions = ['select_photo']
    inherit_actions = False

    def queryset(self, request, basecontent=None):
        return Photo.objects.exclude(carousel=self.basecontent)

    def select_photo(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        if selected:
            if request.POST.get('post'):
                basecontent = self.basecontent
                for selected_photo in queryset:
                    basecontent.photo_list.add(selected_photo)
                return
            extra_context = {'title': _(u'Are you sure you want to select these photos?'),
                             'action_submit': 'select_photo'}
            return self.confirm_action(request, queryset, extra_context)
    select_photo.short_description = _("Select photo")


class DocumentSectionModelAdmin(BaseAdmin):
    ordering = ('position', )


def register(site):
    site.register(Section, SectionAdmin)
    site.register(AppSection, AppSectionAdmin)
    site.register(Carousel, CarouselAdmin)
    site.register(DocumentSection, DocumentSectionModelAdmin)
    site.register_related(Photo, CarouselPhotoRelatedModelAdmin, related_to=Carousel)
    site.register_related(Photo, CarouselRelatedChoosePhotoModelAdmin, related_to=Carousel)
    site.register_related(Document, DocumentRelatedModelAdmin, related_to=Section)
    site.register_related(CustomStyle, CustomStyleRelatedModelAdmin, related_to=Section)
    site.register_related(Menu, MainMenuRelatedAdmin, related_to=Section)
    site.register_related(Menu, SecondaryMenuRelatedAdmin, related_to=Section)
