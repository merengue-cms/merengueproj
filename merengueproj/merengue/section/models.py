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

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import permalink, Q
from django.db.models.signals import post_save
from django.template import defaultfilters
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

import mptt

from merengue.base.managers import WorkflowManager
from merengue.base.models import BaseContent
from merengue.cache import memoize, MemoizeCache
from merengue.section.managers import SectionManager
from merengue.perms.models import Role
from merengue.perms import utils as perms_api
from merengue.viewlet.models import RegisteredViewlet
from transmeta import TransMeta, get_fallback_fieldname


_menu_sections_cache = MemoizeCache('menu_sections')


def _convert_cache_args(mem_args):
    item_class = mem_args[0]
    return item_class.pk


class RealInstanceMixin(object):

    check_attributes = tuple()

    @property
    def real_instance(self):
        if self.check_attributes:
            for check_attribute in self.check_attributes:
                if hasattr(self, check_attribute):
                    child_self = getattr(self, check_attribute, self)
                    if self == child_self:
                        return  getattr(self, check_attribute, self)
                    else:
                        return child_self.real_instance

        # try looking in our cache
        if hasattr(self, '_real_instance'):
            return self._real_instance
        # python & django magic to get the real attributes of the object
        field_names = self._meta.get_all_field_names()
        keys = [k for k in self.__dict__.keys() if k in field_names]

        for key in keys:
            field_names.remove(key)

        # get the internal object that is a subclass of ourselves: sounds
        # weird and *it is* weird. See Django subclassing tale for better
        # understanding.
        for field_name in field_names:
            try:
                obj = getattr(self, field_name)
                if isinstance(obj, self.__class__):
                    self._real_instance = obj
                    return self._real_instance
            except (ObjectDoesNotExist, AttributeError):
                pass
        return self


class Menu(models.Model):

    __metaclass__ = TransMeta

    name = models.CharField(
        verbose_name=_('name'),
        max_length=200,
        )

    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=200,
        blank=False,
        null=False,
        )

    help_text = models.CharField(
        verbose_name=_('help text'),
        help_text=_('text for describing the menu target, usually placed as link title attribute'),
        max_length=200,
        blank=True,
        null=True,
        )

    parent = models.ForeignKey('Menu',
        verbose_name=_('Parent'),
        blank=True,
        null=True,
        related_name='child_set',
        )

    url = models.URLField(
        verbose_name=_('url'),
        blank=True,
        null=True,
        editable=False,
        )

    status = models.CharField(
        verbose_name=_('status'),
        help_text=_('status of the menu element'),
        choices=(('public', _('public')), ('draft', _('draft'))),
        default='public',
        max_length=25,
    )

    visible_by_roles = models.ManyToManyField(
        Role,
        related_name='visible_menus',
        verbose_name=_('visible menus'),
        blank=True,
        null=True,
        help_text=_('The roles that will see this menu')
    )

    class Meta:
        verbose_name = _('menu')
        verbose_name_plural = _('menus')
        translate = ('name', 'help_text', )

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        if self.url == None:
            self.update_url()
        return self.url

    @permalink
    def get_admin_absolute_url(self):
        """ Link to the admin page for editing the object """
        section = self.get_section()
        if section:
            section_content_type = ContentType.objects.get_for_model(section)
            return ('merengue.base.views.admin_link', [section_content_type.id, section.id, 'mainmenu/%s/' % self.id])
        else:
            menu_content_type = ContentType.objects.get_for_model(self)
            print menu_content_type.id
            print self.id
            return ('merengue.base.views.admin_link', [menu_content_type.id, self.id, ''])

    @permalink
    def menu_public_link_with_out_section(self, ancestors_path):
        return self._menu_public_link_without_section(self, ancestors_path)

    def _menu_public_link_without_section(self, ancestors_path):
        return ('menu_view', (ancestors_path, self.slug))

    @permalink
    def public_link(self):
        menus_ancestors = [menu.slug for menu in self.get_ancestors()][1:]  # first is a dummy root menu and we discard it
        ancestors_path = menus_ancestors and '/%s' % '/'.join(menus_ancestors) or ''
        section = self.get_section()
        if section:
            return section.get_real_instance()._menu_public_link(ancestors_path, self)
        else:
            return self._menu_public_link_without_section(ancestors_path)

    def update_url(self, commit=True):
        try:
            self.url = self.public_link()
        except BaseLink.DoesNotExist:
            self.url = ''
        if commit:
            self.save()
        return self.url

    def is_published(self):
        try:
            return self.baselink.is_published()
        except BaseLink.DoesNotExist:
            return True

    def _get_section(self):
        try:
            return getattr(self, 'main_menu_section')
        except BaseSection.DoesNotExist:
            pass

        if self.parent is not None:
            return self.parent.get_section()
    get_section = memoize(_get_section, _menu_sections_cache, 1, convert_args_func=_convert_cache_args)

    def get_breadcrumbs(self):
        """ Menu breadcrumbs (not included itself) """
        bc = []
        for parent in self.get_ancestors()[1:]:
            url = parent.get_absolute_url()
            bc.append((url, unicode(parent)))

        section = self.get_section()
        if section:
            bc.insert(0, (section.get_absolute_url(), unicode(section)))
        return bc

    def get_ancestors_by_user(self, user=None):
        from merengue.perms.utils import can_manage_site
        ancestors = self.get_ancestors().filter(status='public')  # uses mptt function
        if user and not can_manage_site(user):
            if not user.is_anonymous():
                roles = Role.objects.filter(principalrolerelation__user=user)
            else:
                roles = Role.objects.filter(slug='anonymous_user')
            ancestors = ancestors.filter(Q(visible_by_roles__isnull=True) |
                                         Q(visible_by_roles__in=roles))
        return ancestors

    def get_descendants_by_user(self, user=None):
        from merengue.perms.utils import can_manage_site
        descendants = self.get_descendants().filter(status='public')  # uses mptt function
        if user and not can_manage_site(user):
            if not user.is_anonymous():
                roles = Role.objects.filter(principalrolerelation__user=user)
            else:
                roles = Role.objects.filter(slug='anonymous_user')
            descendants = descendants.filter(Q(visible_by_roles__isnull=True) |
                                             Q(visible_by_roles__in=roles)).distinct()
        return descendants

    def can_edit(self, user):
        section = self.get_section()
        if section:
            return section.can_edit(user)
        else:
            return perms_api.can_manage_site(user)


try:
    mptt.register(Menu)
except mptt.AlreadyRegistered:
    pass


class BaseLink(models.Model, RealInstanceMixin):

    menu = models.OneToOneField(
        Menu,
        verbose_name=_('menu'),
        )

    def get_absolute_url(self):
        return self.real_instance.get_absolute_url()

    def get_link_tag(self):
        name = self.menu.name
        return u"<a href='%s'>%s</a>" % (self.get_absolute_url(), name)

    def get_breadcrumbs(self):
        return self.menu.get_breadcrumbs()

    class Meta:
        abstract = False

    def is_published(self):
        return self.real_instance.is_published()


class AbsoluteLink(BaseLink):

    url = models.CharField(
        verbose_name=_('url'),
        max_length=200,
        help_text=_('The absolute urls have to write complety: Protocol, domain, query'),
    )

    target_blank = models.BooleanField(
        verbose_name=_('open in new window'),
        blank=True,
        default=False,
    )

    link_class = models.CharField(
        verbose_name=_('css class for this link'),
        max_length=200,
        blank=True,
        null=True,
    )

    def get_absolute_url(self):
        return self.url

    def is_published(self):
        return True


class ContentLink(BaseLink):

    content = models.ForeignKey(
        BaseContent,
        verbose_name=_('Content'),
    )

    def get_absolute_url(self):
        assert self.content is not None
        return self.content.get_absolute_url()

    def is_published(self):
        return self.content.is_published()


class ViewletLink(BaseLink):

    viewlet = models.ForeignKey(RegisteredViewlet, verbose_name=_('Viewlet'))

    def get_absolute_url(self):
        assert self.viewlet is not None
        return self.menu.get_absolute_url()

    def is_published(self):
        return True


class BaseSection(BaseContent):

    order = models.IntegerField(
        _('order'),
        blank=True,
        null=True,
        editable=False,
    )

    main_menu = models.OneToOneField(
        Menu,
        verbose_name=_('main menu'),
        blank=True,
        null=True,
        related_name='main_menu_section',
        editable=False,
    )

    main_content = models.ForeignKey(
        BaseContent,
        null=True,
        blank=True,
        verbose_name=_('main content'),
        help_text=_('content selected here will be shown when entering the section'),
        related_name='section_main_content',
        on_delete=models.SET_NULL,
    )

    related_content = models.ManyToManyField(
        BaseContent,
        related_name='sections',
        verbose_name=_('related contents'),
        editable=False,
        through='SectionRelatedContent',
    )

    customstyle = models.ForeignKey(
        'CustomStyle',
        null=True,
        blank=True,
        editable=False,
        verbose_name=_('custom style'),
        on_delete=models.SET_NULL,
    )

    objects = SectionManager()

    class Meta:
        ordering = ('order', )
        verbose_name = _('section')
        verbose_name_plural = _('sections')
        check_slug_uniqueness = True

    def __unicode__(self):
        return unicode(self.name)

    def get_parent_for_permissions(self):
        """ The section has not parents. Returns None to avoid execute a uneeded SQL """
        return None

    @property
    def check_attributes(self):
        return [subcl._meta.module_name for subcl in self.__class__.__subclasses__()]

    def public_link(self):
        url = super(BaseSection, self).public_link()
        return strip_section_prefix(url)

    def _public_link_without_section(self):
        return ('section_view', [self.slug])

    def get_breadcrumbs(self):
        return [(self.get_absolute_url(), unicode(self))]

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self)
        return ('merengue.base.views.admin_link', [content_type.id, self.id, ''])

    @permalink
    def content_public_link(self, section, content):
        return self._content_public_link(section, content)

    def _content_public_link(self, section, content):
        return ('content_section_view', [section.slug, content.id, content.slug])

    @permalink
    def document_public_link(self, section, content):
        return self._document_public_link(section, content)

    def _document_public_link(self, section, content):
        return ('document_section_view', [section.slug, content.id, content.slug])

    @permalink
    def menu_public_link(self, ancestors_path, menu):
        return self._menu_public_link(ancestors_path, menu)

    def _menu_public_link(self, ancestors_path, menu):
        return ('menu_section_view', (self.slug, ancestors_path, menu.slug))

    def has_custom_style(self):
        return bool(self.customstyle)

    def breadcrumbs_items(self):
        return [(unicode(self), self.get_absolute_url())]

    def breadcrumbs(self, content=None):
        urls = self.breadcrumbs_items()
        if content:
            urls.append((unicode(content), ''))
        return render_to_string('section/breadcrumbs.html', {'urls': urls})

    def url_in_section(self, url):
        return url


def strip_section_prefix(link):
    section_index_url = reverse('section_index')[:-1]
    return link.replace('%s' % section_index_url, '')


def sections_permalink(func):

    def inner(*args, **kwargs):
        bits = func(*args, **kwargs)
        link = reverse(bits[0], None, *bits[1:3])
        return strip_section_prefix(link)
    return inner


class SectionRelatedContent(models.Model):
    basesection = models.ForeignKey(BaseSection, related_name='sectionrelatedcontent')
    basecontent = models.ForeignKey(BaseContent)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'section_basesection_related_content'


class Document(BaseContent):

    objects = WorkflowManager()

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        content_view_template = 'section/document_view.html'

    def __unicode__(self):
        return unicode(self.name)

    @permalink
    def public_link(self):
        section = self.get_main_section()
        if not section:
            return self._public_link_without_section()
        return section.get_real_instance()._document_public_link(section, self)


class DocumentSection(models.Model):

    __metaclass__ = TransMeta

    document = models.ForeignKey(
        Document,
        verbose_name=_('Parent document'),
        related_name='document_sections',
        )

    position = models.IntegerField(
        editable=False,
        )

    body = models.TextField(
        verbose_name=_('body'),
        blank=True,
        default='',
        )

    class Meta:
        verbose_name = _('document section')
        verbose_name_plural = _('document sections')
        translate = ('body', )
        ordering = ('position', )

    def _flexisave(self):
        return super(DocumentSection, self).save()

    def _flexidelete(self):
        super(DocumentSection, self).delete()

    def _get_team(self):
        return self.document.team

    team = property(_get_team)

    def move_to(self, pos):
        try:
            DocumentSection.objects.get(document=self.document, position=pos)
        except DocumentSection.DoesNotExist:
            raise ValueError(_('Can not move to non existing position'))

        if pos > self.position:
            for i in DocumentSection.objects.filter(document=self.document, position__in=range(self.position + 1, pos + 1)):
                i.position -= 1
                i._flexisave()
        elif pos < self.position:
            for i in DocumentSection.objects.filter(document=self.document, position__in=range(pos, self.position)):
                i.position += 1
                i._flexisave()
        else:
            return
        self.position = pos
        self._flexisave()

    def save(self, *args, **kwargs):
        count = DocumentSection.objects.filter(document=self.document).count()
        if self.position == None:
            self.position = count
        elif self.position >= count:
            self.position = count - 1
        try:
            existing_position = DocumentSection.objects.get(document=self.document, position=self.position)
            if existing_position.id != self.id:
                raise ValueError(_('Trying to save DocumentSection into an existing position'))
        except DocumentSection.DoesNotExist:
            pass

        return super(DocumentSection, self).save(*args, **kwargs)

    def delete(self):
        pos = self.position
        doc = self.document
        super(DocumentSection, self).delete()

        for i in DocumentSection.objects.filter(document=doc, position__gt=pos):
            i.position -= 1
            i._flexisave()

    def __unicode__(self):
        return u'%s - Section %s' % (self.document, self.position)


class CustomStyle(models.Model):

    css_chunk = models.TextField(
        verbose_name=_('css chunk'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('custom sytle')
        verbose_name_plural = _('custom styles')


class CustomStyleImage(models.Model):
    customstyle = models.ForeignKey(CustomStyle)

    custom_css_image = models.ImageField(
        verbose_name=_('Custom CSS image'),
        upload_to='section_images',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('custom sytle image')
        verbose_name_plural = _('custom style images')


def create_menus(sender, **kwargs):
    if issubclass(sender, BaseSection):
        created = kwargs.get('created', False)
        instance = kwargs.get('instance')

        if created:
            menu_name = 'Main menu of %s' % unicode(instance)
            instance.main_menu = Menu.objects.create(**{'slug': defaultfilters.slugify(menu_name),
                                                        get_fallback_fieldname('name'): menu_name})
            from merengue.cache import invalidate_johnny_cache
            invalidate_johnny_cache(instance.__class__, True, BaseSection)
            instance.save()


post_save.connect(create_menus, dispatch_uid='SectionMenusSignalDispatcher')


def handle_link_url_post_save(sender, instance, **kwargs):
    linklist = []
    if isinstance(instance, BaseLink):
        linklist = [instance]
    elif isinstance(instance, BaseSection):
        for content in instance.related_content.all():
            linklist += content.contentlink_set.all()
    elif isinstance(instance, BaseContent):
        linklist = instance.contentlink_set.all()

    for link in linklist:
        if link and link.get_absolute_url() != link.menu.url:
            link.menu.update_url()

post_save.connect(handle_link_url_post_save)


def handle_menu_url_post_save(sender, instance, **kwargs):
    url = instance.url
    instance.update_url(commit=False)
    if instance and url != instance.url:
        instance.save()

post_save.connect(handle_menu_url_post_save, sender=Menu)
