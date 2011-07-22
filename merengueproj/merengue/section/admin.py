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
from django.db.models import Q
from django import forms
from django.forms.util import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from ajax_select.fields import AutoCompleteSelectField
from transmeta import get_real_fieldname_in_each_language, get_fallback_fieldname

from merengue.base.admin import (BaseAdmin, BaseContentAdmin,
                                 RelatedModelAdmin, OrderableRelatedModelAdmin)
from merengue.section.fields import CSSValidatorField
from merengue.section.forms import MenuAdminModelForm
from merengue.section.models import (Menu, BaseSection,
                                     BaseLink, AbsoluteLink, ContentLink, ViewletLink,
                                     Document, DocumentSection, CustomStyle,
                                     SectionRelatedContent, CustomStyleImage)
from merengue.section.formsets import BaseLinkInlineFormSet
from merengue.perms import utils as perms_api
from merengue.perms.admin import PermissionAdmin


class BaseSectionAdmin(BaseContentAdmin, PermissionAdmin):
    sortablefield = 'order'
    ordering = ('order', )
    list_display = BaseContentAdmin.list_display[:-1]
    search_fields = tuple(get_real_fieldname_in_each_language('name'))
    html_fields = ()
    removed_fields = ('description', )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}
    exclude = BaseContentAdmin.exclude + ('commentable', )

    def get_object(self, request, object_id):
        """
        Overrides the django behaviour
        """
        queryset = self.queryset(request, bypass_perms=True)
        model = queryset.model
        try:
            object_id = model._meta.pk.to_python(object_id)
            return queryset.get(pk=object_id)
        except (model.DoesNotExist, ValidationError):
            return None

    def queryset(self, request, bypass_perms=False):
        """
        Overrides the Django behaviour to take permissions into account
        """
        qs = super(BaseSectionAdmin, self).queryset(request)
        if not bypass_perms and not perms_api.can_manage_site(request.user) and \
           not perms_api.has_global_permission(request.user, 'edit'):
            qs = qs.filter(Q(owners=request.user))
        return qs

    def has_add_permission(self, request):
        """
            Overrides Django admin behaviour to add ownership based access control
        """
        return perms_api.has_global_permission(request.user, 'manage_section')

    def has_change_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        permission = super(BaseSectionAdmin, self).has_change_permission(request, obj)
        if permission:
            return permission
        if perms_api.has_global_permission(request.user, 'manage_section'):
            return True
        elif obj is None:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Overrides Django admin behaviour to add ownership based access control
        """
        return perms_api.has_global_permission(request.user, 'manage_section')

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseSectionAdmin, self).get_form(request, obj, **kwargs)
        if 'main_content' in form.base_fields.keys():
            field = form.base_fields['main_content']
            qs = field.queryset
            if not obj:
                qs = qs.model.objects.get_empty_query_set()
            else:
                qs = qs.filter(sections=obj)

            # Como Document no esta registrado en el admin site, no tiene
            # sentido mostrar este campo si no tiene opciones ya que no
            # se pueden crear nuevos documentos desde aqui
            if qs.count():
                field.queryset = qs
            else:
                form.base_fields.pop('main_content')
        return form


class AbsoluteLinkAdmin(BaseAdmin):
    list_display = ('url', )


class ContentLinkAdmin(BaseAdmin):
    list_display = ('content', )


class ViewletLinkAdmin(BaseAdmin):
    list_display = ('viewlet', )


class SectionAdmin(BaseSectionAdmin):

    change_list_template = 'admin/section/section/change_list.html'
    change_form_template = 'admin/section/section/change_form.html'

    def get_form(self, request, obj=None, **kwargs):
        form = super(SectionAdmin, self).get_form(request, obj, **kwargs)
        if 'section' in form.base_fields:
            del form.base_fields['section']
        if 'main_content' in form.base_fields.keys():
            link_autocomplete = AutoCompleteSelectField(
                'section_contentlink', label=ugettext('main content'),
            )
            link_autocomplete.widget.help_text = ugettext('content selected here will be shown when entering the section')
            form.base_fields['main_content'] = link_autocomplete
        return form

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['change_form_section'] = True
        return super(SectionAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def get_section_tools(self, model, tools=None):
        tools = tools or []
        if model in self.admin_site.tools:
            tools.extend([val for key, val in self.admin_site.tools[model].items() if getattr(val, 'manage_contents', False)])
        else:
            for parent in model._meta.parents:
                tools.extend(self.get_section_tools(parent, tools))
        return tools

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        section_tools = self.get_section_tools(self.model)
        extra_context.update({'section_tools': section_tools})
        return super(SectionAdmin, self).changelist_view(request, extra_context)


class SectionContentAdmin(OrderableRelatedModelAdmin):
    related_field = 'sections'
    sortablefield = 'order'
    manage_contents = True

    def get_form(self, request, obj=None, **kwargs):
        form = super(SectionContentAdmin, self).get_form(request, obj, **kwargs)
        if 'section' in form.base_fields:
            # the section should be not editable because the content
            # is in a admin related to this section. we remove the field
            del form.base_fields['section']
        return form

    def custom_relate_content(self, request, obj, form, change):
        if not change:
            SectionRelatedContent.objects.create(
                basesection=self.basecontent,
                basecontent=obj)

    def get_relation_obj(self, through_model, obj):
        return through_model.objects.get(basesection=self.basecontent, basecontent=obj)


class CustomStyleImageInline(admin.StackedInline):
    model = CustomStyleImage


class CustomStyleRelatedModelAdmin(RelatedModelAdmin):
    tool_name = 'style'
    tool_label = _('custom style')
    related_field = 'basesection'
    one_to_one = True
    inlines = [CustomStyleImageInline]
    change_form_template = 'admin/section/customstyle/change_form.html'

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(CustomStyleRelatedModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'css_chunk':
            required = not db_field.null
            formfield = CSSValidatorField(db_field.name, kwargs['request'], required=required)
            formfield.help_text = _('Custom style for the section. You can use the variables $media_url and $theme_url')
        return formfield

    def has_delete_permission(self, request, obj=None):
        return False


class DocumentAdmin(BaseContentAdmin):
    list_display = ('name', 'slug', 'workflow_status', )
    html_fields = ('description', 'body', )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}
    actions = BaseAdmin.actions + ['set_as_published', 'set_as_draft']


class DocumentRelatedModelAdmin(SectionContentAdmin, DocumentAdmin):
    tool_name = 'documents'
    tool_label = _('documents')
    manage_contents = True


class BaseLinkInline(admin.TabularInline):

    extra = 0
    formset = BaseLinkInlineFormSet

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
        return formset


class AbsoluteLinkInline(BaseLinkInline):
    model = AbsoluteLink
    max_num = 1
    extra = 1
    verbose_name = _('Menu Absolute Link')
    verbose_name_plural = _('Menu Absolute Links')

    def _media(self):
        js = []
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
            field.label = "%s (%s)" % (unicode(field.label), unicode(field.help_text))

            def clean(value):
                return value
            field.clean = clean
        return field


class ContentLinkInline(BaseLinkInline):
    model = ContentLink
    max_num = 1
    extra = 1
    verbose_name = _('Menu Content Link')
    verbose_name_plural = _('Menu Content Links')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(ContentLinkInline, self).get_formset(request, obj, **kwargs)
        if not formset:
            return formset
        form = formset.form
        if 'content' in form.base_fields.keys():
            link_autocomplete = AutoCompleteSelectField(
                'section_contentlink', label=ugettext('Content'),
            )
            link_autocomplete.widget.help_text = ugettext('Enter text to search the content')
            form.base_fields['content'] = link_autocomplete
        return formset


class ViewletLinkInline(BaseLinkInline):
    model = ViewletLink
    max_num = 1
    verbose_name = _('Menu Viewlet Link')
    verbose_name_plural = _('Menu Viewlet Links')


class MenuAdmin(BaseAdmin):
    list_display = ('level', 'display_move_to', 'name', 'slug', )
    list_display_links = ('name', )
    prepopulated_fields = {'slug': (get_fallback_fieldname('name'), )}
    ordering = ('lft', )
    actions = []
    inherit_actions = False
    inlines = [AbsoluteLinkInline, ContentLinkInline, ViewletLinkInline]
    form = MenuAdminModelForm
    menu_slug = None

    class Media:
        css = {'all': ('merengue/css/ajaxautocompletion/jquery.autocomplete.css',
                       'merengue/css/ajax_select/iconic.css')}
        js = ('merengue/js/ajaxautocompletion/jquery.autocomplete.js',
              'merengue/js/ajax_select/ajax_select.js')

    def __init__(self, *args, **kwargs):
        super(MenuAdmin, self).__init__(*args, **kwargs)
        self.old_inline_instances = [instance for instance in self.inline_instances]

    def get_menu(self, request, *args, **kwargs):
        return Menu.tree.get(slug=self.menu_slug or settings.MENU_PORTAL_SLUG)

    def queryset(self, request):
        return self.get_menu(request).get_descendants()

    def has_add_permission(self, request):
        """
            Overrides Django admin behaviour to add ownership based access control
        """
        return perms_api.has_global_permission(request.user, 'manage_menu')

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
    display_move_to.allow_tags = True

    def get_formsets(self, request, obj=None):
        self.inline_instances = []
        res = []
        for inline in self.old_inline_instances:
            formset = inline.get_formset(request, obj)
            if formset:
                self.inline_instances.append(inline)
                res.append(formset)
        return res

    def get_form(self, request, obj=None, **kwargs):
        form = super(MenuAdmin, self).get_form(request, obj, **kwargs)
        form.section = getattr(self, 'basecontent', None)
        return form

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
        media.add_js([settings.MEDIA_URL + "merengue/js/section/CollapsableMenuTree.js"])
        extra_context.update({'media': media.render(),
                              'moved_source': source})
        return super(MenuAdmin, self).changelist_view(request, extra_context)


class BaseSectionMenuRelatedAdmin(MenuAdmin, RelatedModelAdmin):
    change_list_template = "admin/section/menu/change_list.html"

    def has_add_permission(self, request):
        return RelatedModelAdmin.has_add_permission(self, request)

    def has_change_permission(self, request, obj=None):
        return RelatedModelAdmin.has_change_permission(self, request, obj)

    def has_delete_permission(self, request, obj=None):
        return RelatedModelAdmin.has_delete_permission(self, request, obj)

    def get_section_docs(self, request):
        section = getattr(self.get_menu(request), self.related_field)
        return section.content_set.all()

    def get_menu(self, request, *args, **kwargs):
        basecontent = kwargs.pop('basecontent', None)
        queryset = RelatedModelAdmin.queryset(self, request, basecontent)
        return queryset and queryset.get() or None

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseSectionMenuRelatedAdmin, self).get_form(request, obj, **kwargs)
        if 'parent' in form.base_fields.keys():
            qs = form.base_fields['parent'].queryset
            qs = qs.filter(tree_id=self.get_menu(request).tree_id, level__gt=0)
            if obj:
                qs = qs.exclude(pk=obj.pk)
            form.base_fields['parent'].queryset = qs
        return form

    def queryset(self, request, basecontent=None):
        """ overrided to get the menu of the content section """
        menu = self.get_menu(request, basecontent)
        if not menu:
            return Menu.tree.get_empty_query_set()
        else:
            return Menu.tree.filter(tree_id=menu.tree_id, level__gt=0)

    def save_model(self, request, obj, form, change):
        if not obj.parent:
            obj.parent = self.get_menu(request)
        super(BaseSectionMenuRelatedAdmin, self).save_model(
            request, obj, form, change,
        )


class MainMenuRelatedAdmin(BaseSectionMenuRelatedAdmin):
    tool_name = 'mainmenu'
    tool_label = _('main menu')
    related_field = 'main_menu_section'

    def changelist_view(self, request, extra_context={}, parent_model_admin=None, parent_object=None):
        extra_context = self._update_extra_context(request, extra_context, parent_model_admin, parent_object)
        return super(MainMenuRelatedAdmin, self).changelist_view(request, extra_context)


class PortalMenuAdmin(MenuAdmin):
    tool_name = 'portalmenu'
    tool_label = _('portal menu')
    related_field = 'parent'

    def get_form(self, request, obj=None, **kwargs):
        form = super(PortalMenuAdmin, self).get_form(request, obj, **kwargs)
        if 'parent' in form.base_fields.keys():
            qs = form.base_fields['parent'].queryset
            root_menu = self.get_menu(request)
            descendants = root_menu.get_descendants()
            qs = descendants and qs.filter(pk__in=descendants.values('pk').query) or descendants
            form.base_fields['parent'].queryset = qs
        return form

    def save_form(self, request, form, change):
        menu = form.save(commit=False)
        if not getattr(menu, self.related_field, None):
            basecontent = Menu.objects.get(slug=self.menu_slug or settings.MENU_PORTAL_SLUG)
            setattr(menu, self.related_field, basecontent)
        return menu


class DocumentSectionModelAdmin(BaseAdmin):
    ordering = ('position', )
    html_fields = ('body', )


class DocumentSectionRelatedModelAdmin(RelatedModelAdmin):
    tool_name = 'document_sections'
    tool_label = _('document sections')
    ordering = ('position', )
    html_fields = ('body', )
    related_field = 'document'


def register_related(site):
    site.register_related(Document, DocumentRelatedModelAdmin, related_to=BaseSection)
    site.register_related(CustomStyle, CustomStyleRelatedModelAdmin, related_to=BaseSection)
    site.register_related(Menu, MainMenuRelatedAdmin, related_to=BaseSection)
    site.register_related(DocumentSection, DocumentSectionRelatedModelAdmin, related_to=Document)


def register(site):
    site.register(BaseSection, SectionAdmin)
    site.register(Document, DocumentAdmin)
    site.register(Menu, PortalMenuAdmin)
    register_related(site)
