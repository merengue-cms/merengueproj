import md5

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from django.template import defaultfilters
from django.utils.translation import ugettext_lazy as _

import mptt

from cmsutils.adminfilters import QueryStringManager

from merengue.base.managers import WorkflowManager
from merengue.base.models import Base, BaseContent
from merengue.section.managers import SectionManager
from merengue.viewlet.models import RegisteredViewlet
from searchform.registry import search_form_registry
from transmeta import TransMeta


class RealInstanceMixin(object):

    check_attributes = tuple()

    @property
    def real_instance(self):
        if self.check_attributes:
            for check_attribute in self.check_attributes:
                if hasattr(self, check_attribute):
                    return  getattr(self, check_attribute, self)

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

    class Meta:
        verbose_name = _('menu')
        verbose_name_plural = _('menus')
        translate = ('name', )

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        if self.url == None:
            self.update_url()
        return self.url

    def update_url(self):
        try:
            menus_ancestors = [menu.slug for menu in self.get_ancestors()][1:] # first is a dummy root menu and we discard it
            ancestors_path = menus_ancestors and '/%s' % '/'.join(menus_ancestors) or ''
            section = self.get_section()
            if section:
                self.url = reverse('menu_section_view', args=(section.slug, ancestors_path, self.slug))
            else:
                self.url = reverse('menu_view', args=(ancestors_path, self.slug))
        except BaseLink.DoesNotExist:
            self.url = ''
        self.save()
        return self.url

    def is_published(self):
        try:
            return self.baselink.is_published()
        except BaseLink.DoesNotExist:
            return True

    def get_section(self):
        try:
            return getattr(self, 'main_menu_section')
        except BaseSection.DoesNotExist:
            pass

        if self.parent is not None:
            return self.parent.get_section()

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

    url = models.URLField(
        verbose_name=_('url'),
        )

    def get_absolute_url(self):
        return self.url

    def is_published(self):
        return True


class ContentLink(BaseLink):

    content = models.ForeignKey(BaseContent, verbose_name=_('Content'))

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


class BaseSection(Base, RealInstanceMixin):

    __metaclass__ = TransMeta

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
        null = True,
        blank = True,
        verbose_name=_('main content'),
        related_name='section_main_content',
    )
    main_content.delete_cascade = False

    related_content = models.ManyToManyField(
        BaseContent,
        verbose_name=_('related contents'),
        editable=False,
        through='SectionRelatedContent',
    )

    customstyle = models.ForeignKey(
        'CustomStyle',
        null = True,
        blank = True,
        editable = False,
        verbose_name=_('custom style'),
    )
    customstyle.delete_cascade = False

    objects = SectionManager()

    class Meta:
        abstract = False
        ordering = ('order', )

    def __unicode__(self):
        return unicode(self.name)

    @property
    def app_name(self):
        return self.real_instance.app_name

    @property
    def check_attributes(self):
        return [subcl._meta.module_name for subcl in self.__class__.__subclasses__()]

    def get_absolute_url(self):
        return strip_section_prefix(self.real_instance.get_absolute_url())

    def get_breadcrumbs(self):
        return [(self.get_absolute_url(), unicode(self))]

    @permalink
    def get_agenda_url(self):
        return ("%s_agenda_view" %(self.app_name), [])

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self)
        return ('merengue.base.views.admin_link', [content_type.id, self.id, ''])

    def has_custom_style(self):
        return bool(self.customstyle)


def strip_section_prefix(link):
    return link.replace('sections/', '')


def sections_permalink(func):

    def inner(*args, **kwargs):
        bits = func(*args, **kwargs)
        link = reverse(bits[0], None, *bits[1:3])
        return strip_section_prefix(link)
    return inner


class SectionRelatedContent(models.Model):
    basesection = models.ForeignKey(BaseSection)
    basecontent = models.ForeignKey(BaseContent)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'section_basesection_related_content'


class Section(BaseSection):
    objects = SectionManager()

    @property
    def app_name(self):
        return ''

    @sections_permalink
    def get_absolute_url(self):
        return ('section_view', (self.slug, ))


class AppSection(BaseSection):
    objects = SectionManager()

    @sections_permalink
    def get_absolute_url(self):
        return ('%s_index' % self.app_name, None, tuple())

    @property
    def app_name(self):
        assert self.slug is not None
        if self.slug not in settings.SECTION_MAP:
            return 'ERROR-NO-REGISTRADO'
        return settings.SECTION_MAP[self.slug]['app_name']


class Document(BaseContent):

    search_form = models.CharField(
        verbose_name=_('search form'),
        max_length=200,
        blank=True,
        null=True,
        editable=False, # until search form feature was completed
    )

    search_form_filters = models.TextField(
        verbose_name=_('searcher options'),
        blank=True,
        null=True,
        editable=False, # until search form feature was completed
    )

    permanent = models.BooleanField(verbose_name=_('permanent'),
                                    help_text=_('make this document not erasable and its slug ummutable'),
                                    editable=False,
                                    default=False,
    )

    objects = WorkflowManager()

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        content_view_template = 'section/document_view.html'

    def __unicode__(self):
        return unicode(self.name)

    def get_search_form(self):
        if self.search_form:
            form_class = search_form_registry.get_form_class(self.search_form)
            qsm = QueryStringManager(None)
            filters = dict([(f, []) for f in self.get_search_form_filters()])
            for filter in filters:
                options = self.get_search_form_filters_options(filter)
                filters[filter] = options
                if search_form_registry.can_select_multiple_options(
                    self.search_form,
                    filter,
                    ):
                    qsm.filters.setlist(filter + '__in', options)
                else:
                    qsm.filters[filter + '__exact'] = options[0]

            form = form_class(query_string_manager=qsm)
            for filter, options in filters.items():
                field = form.fields[filter]
                field.filters['id__in'] = options

            return form

    def get_search_form_filters(self):
        if not self.search_form_filters:
            return []
        result = []
        for filter_and_options in self.search_form_filters.split('\n'):
            if filter_and_options:
                result.append(filter_and_options.split(':')[0].strip())
        return result

    def get_search_form_filters_options(self, filter_name):
        if not self.search_form_filters:
            return []
        for filter_and_options in self.search_form_filters.split('\n'):
            if filter_and_options:
                (name, options) = filter_and_options.split(':')
                name=name.strip()
                if name == filter_name:
                    option_list = []
                    for option in options.split(','):
                        soption = option.strip()
                        if soption.isdigit():
                            option_list.append(int(soption))
                        else:
                            option_list.append(soption)
                    return option_list
        return []

    def get_cache_key(self):
        """ returns a cache key that identifies this document with search form
            configuration set """
        cache_key = ''
        if self.related_section:
            cache_key += self.related_section.slug
        cache_key += self.search_form
        cache_key += md5.md5(self.search_form_filters or '').hexdigest()
        return cache_key

    @permalink
    def public_link(self):
        return ('document_section_view', [self.get_main_section().slug, self.id, self.slug])


class DocumentSection(models.Model):

    __metaclass__ = TransMeta

    document = models.ForeignKey(
        Document,
        verbose_name=_('Parent document'),
        related_name='sections',
        )

    position = models.IntegerField(
        editable=False,
        )

    body = models.TextField(
        verbose_name=_('body'),
        blank=True,
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
            existing_position = DocumentSection.objects.get(document=self.document, position=pos)
        except DocumentSection.DoesNotExist:
            raise ValueError(_('Can not move to non existing position'))


        if pos > self.position:
            for i in DocumentSection.objects.filter(document=self.document, position__in=range(self.position+1, pos+1)):
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
            self.position = count-1
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
    pass


def create_menus(sender, **kwargs):
    created = kwargs.get('created', False)
    instance = kwargs.get('instance')

    if created:
        menu_name = 'Main menu of %s' % unicode(instance)
        instance.main_menu = Menu.objects.create(
            name_es=menu_name,
            slug=defaultfilters.slugify(menu_name),
        )
        instance.save()

post_save.connect(create_menus, sender=Section, dispatch_uid='SectionMenusSignalDispatcher')
post_save.connect(create_menus, sender=AppSection, dispatch_uid='AppSectionMenusSignalDispatcher')


def handle_link_url_post_save(sender, instance, **kwargs):
    linklist = []
    if isinstance(instance, BaseLink):
        linklist = [instance]
    elif isinstance(instance, BaseContent):
        linklist = instance.contentlink_set.all()
    elif isinstance(instance, BaseSection):
        for content in instance.related_content.all():
            linklist += content.contentlink_set.all()

    for link in linklist:
        if link and link.get_absolute_url() != link.menu.url:
            link.menu.update_url()

post_save.connect(handle_link_url_post_save)
