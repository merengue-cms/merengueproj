import md5

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

import mptt

from cmsutils.adminfilters import QueryStringManager
from cmsutils.db.fields import ColorField

from merengue.base.managers import WorkflowManager
from merengue.base.models import Base, BaseContent
from merengue.multimedia.models import Photo, Video
from searchform.registry import search_form_registry
from stdimage import StdImageField
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
        #if self.url == None:
        self.update_url()
        return self.url

    def update_url(self):
        try:
            menus_ancestors = ('/').join([menu.slug for menu in self.get_ancestors()])
            self.url = reverse('menu_section_view', args=(self.get_section().slug, menus_ancestors, self.slug))
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
        for menu_attr in ('main_menu_section', 'interest_menu_section', 'secondary_menu_section'):
            try:
                return getattr(self, menu_attr)
            except BaseSection.DoesNotExist:
                pass

        if self.parent is not None:
            return self.parent.get_section()

    def get_breadcrumbs(self):
        bc = [(self.get_absolute_url(), unicode(self))]
        parent = self.parent
        while parent is not None and parent.parent is not None:
            url = parent.get_absolute_url()
            if url is None: # the first menu node does not have link
                break
            bc.append((url, unicode(parent)))
            parent = parent.parent

        section = self.get_section()
        bc.append((section.get_absolute_url(), unicode(section)))

        bc.reverse()
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

    content = models.OneToOneField(BaseContent,
        verbose_name=_('Content'),
        )

    def get_absolute_url(self):
        assert self.content is not None
        return self.content.get_absolute_url()

    def is_published(self):
        return self.content.is_published()


class BaseSection(Base, RealInstanceMixin):

    __metaclass__ = TransMeta

    main_menu = models.OneToOneField(
        Menu,
        verbose_name=_('main menu'),
        blank=True,
        null=True,
        related_name='main_menu_section',
        editable=False,
    )

    secondary_menu = models.OneToOneField(
        Menu,
        verbose_name=_('secondary menu'),
        blank=True,
        null=True,
        related_name='secondary_menu_section',
        editable=False,
    )

    interest_menu = models.OneToOneField(
        Menu,
        verbose_name=_('interest menu'),
        blank=True,
        null=True,
        related_name='interest_menu_section',
        editable=False,
    )

    main_menu_template = models.CharField(
        _('custom main menu template'),
        max_length=200,
        blank=True,
        null=True,
        editable=False,
    )

    secondary_menu_template = models.CharField(
        _('custom secondary menu template'),
        max_length=200,
        blank=True,
        null=True,
        editable=False,
    )

    interest_menu_template = models.CharField(
        _('custom interest menu template'),
        max_length=200,
        blank=True,
        null=True,
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
    )

    customstyle = models.ForeignKey(
        'CustomStyle',
        null = True,
        blank = True,
        editable = False,
        verbose_name=_('custom style'),
    )
    customstyle.delete_cascade = False

    objects = WorkflowManager()

    class Meta:
        abstract = False

    def __unicode__(self):
        return unicode(self.name)

    @property
    def app_name(self):
        return self.real_instance.app_name

    @property
    def check_attributes(self):
        return [subcl._meta.module_name for subcl in self.__class__.__subclasses__()]

    def get_absolute_url(self):
        return self.real_instance.get_absolute_url()

    def get_breadcrumbs(self):
        return [(self.get_absolute_url(), unicode(self))]

    @permalink
    def get_agenda_url(self):
        return ("%s_agenda_view" %(self.app_name), [])

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self)
        return ('base.views.admin_link', [content_type.id, self.id, ''])

    def has_custom_style(self):
        return bool(self.customstyle)


def strip_section_prefix(link):
    return link.replace('secciones/', '')


def sections_permalink(func):

    def inner(*args, **kwargs):
        bits = func(*args, **kwargs)
        link = reverse(bits[0], None, *bits[1:3])
        return strip_section_prefix(link)
    return inner


class Section(BaseSection):
    objects = WorkflowManager()

    @property
    def app_name(self):
        return ''

    @sections_permalink
    def get_absolute_url(self):
        return ('section_view', (self.slug, ))


class AppSection(BaseSection):

    @sections_permalink
    def get_absolute_url(self):
        return ('%s_index' % self.app_name, None, tuple())

    @property
    def app_name(self):
        assert self.slug is not None
        if self.slug not in settings.SECTION_MAP:
            return 'ERROR-NO-REGISTRADO'
        return settings.SECTION_MAP[self.slug]['app_name']


class Carousel(models.Model):

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

    photo_list = models.ManyToManyField(Photo,
        verbose_name=_('photos'),
        blank=True,
        null=True,
        )

    class_name = models.ManyToManyField(ContentType,
        verbose_name=_('class name'),
        blank=True,
        null=True,
        )

    def photos(self):
        return self.photos_bag()

    def photos_bag(self, bag=50):
        return self.photo_list.all()[:bag]

    def render(self):
        render_string = render_to_string('base/photos_secundary_carousel.html',
                        {'photos': self.photos(),
                        'MEDIA_URL': getattr(settings, 'MEDIA_URL', '/media/'),
                        'LANGUAGE_CODE': getattr(settings, 'LANGUAGE_CODE', 'es'),
                         },
                        )
        return render_string

    def __unicode__(self):
        return unicode(self.name)


class Document(BaseContent):

    __metaclass__ = TransMeta

    body = models.TextField(
        verbose_name=_('body'),
        )

    photo = StdImageField(
        verbose_name=_('photo'),
        upload_to='document_photos',
        thumbnail_size=(200, 200),
        blank=True,
        null=True,
        )

    floatimage = models.BooleanField(
        verbose_name=_('float image'),
        help_text=_('make image float in view'),
        blank=True,
        default=False,
    )

    photo_description = models.CharField(
        verbose_name=_('photo description'),
        max_length=200,
        blank=True,
        null=True,
        )

    carousel = models.ForeignKey(
        Carousel,
        verbose_name=_('carousel'),
        blank=True,
        null=True,
        )
    carousel.delete_cascade = False

    videos = models.ManyToManyField(
        Video,
        verbose_name=_('videos'),
        blank=True,
        null=True,
        )

    search_form = models.CharField(
        verbose_name=_('search form'),
        max_length=200,
        blank=True,
        null=True,
        )

    search_form_filters = models.TextField(
        verbose_name=_('searcher options'),
        blank=True,
        null=True,
        )

    related_section = models.ForeignKey(BaseSection,
        verbose_name=_('related section'),
        blank=True,
        null=True,
        )

    permanent = models.BooleanField(verbose_name=_('permanent'),
                                    help_text=_('make this document not erasable and its slug ummutable'),
                                    editable=False,
                                    default=False)

    objects = WorkflowManager()

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        translate = ('body', 'photo_description', )

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        # do not use permalink here since this method is dynamic
        related_section = self.get_related_section()

        if isinstance(related_section.real_instance, AppSection):
            args = (self.slug, )
            app_name = related_section.real_instance.app_name
            url = reverse('%s_document_view' % app_name, None, args)
        else:
            args = (self.related_section.slug, self.slug)
            url = reverse('document_view', None, args)

        return strip_section_prefix(url)

    def get_admin_absolute_url(self):
        # if you dont have related_section you are a subclass of document
        # and you need to overwrite this method
        related_section = self.related_section
        if not related_section:
            raise NotImplemented
        url = 'admin/section/document/%d/' % self.id
        base_url = related_section.real_instance.get_admin_absolute_url()
        return u'%s%s' % (base_url, url)

    def get_related_section(self):
        # if you dont have related_section you are a subclass of document
        # and you need to overwrite this method
        if not self.related_section:
            raise NotImplemented
        return self.related_section

    def get_breadcrumbs(self):
        try:
            link = self.contentlink
        except ContentLink.DoesNotExist:
            link = None
        bc = []
        if link is None:
            bc = self.get_related_section().get_breadcrumbs()
        else:
            bc = link.get_breadcrumbs()
            bc.pop() # the last one is this document

        bc.append((self.get_absolute_url(), unicode(self)))
        return bc

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

    def _get_real_instance(self):
        # try looking in our cache
        if hasattr(self, '_real_instance'):
            return self._real_instance

        # python & django magic to get the real attributes of the object
        field_names = self._meta.get_all_field_names()
        keys = [k for k in self.__dict__.keys() if k in field_names]
        # manytomany field to ourselves are hard

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
            except (ObjectDoesNotExist, AttributeError, ValueError):
                pass


class CustomStyle(models.Model):
    color_1 = ColorField(
        verbose_name=_('color 1'),
        null = True,
        blank = True,
        )

    color_2 = ColorField(
        verbose_name=_('color 2'),
        null = True,
        blank = True,
        )

    color_3 = ColorField(
        verbose_name=_('color 3'),
        null = True,
        blank = True,
        )

    menu_link_color = ColorField(
        verbose_name=_('menu link color'),
        null = True,
        blank = True,
        )

    searcher_left_arrow = models.ImageField(
        verbose_name= ('searcher left arrow'),
        upload_to='sections_styles',
        null=True,
        blank=True,
        help_text=_('An arrow pointing to the left for multiple select widgets. (11x11)'),
        )

    searcher_right_arrow = models.ImageField(
        verbose_name= ('searcher right arrow'),
        upload_to='sections_styles',
        null=True,
        blank=True,
        help_text=_('An arrow pointing to the right for multiple select widgets. (11x11)'),
        )

    searcher_tab_image = models.ImageField(
        verbose_name= ('searcher tab image'),
        upload_to='sections_styles',
        null=True,
        blank=True,
        help_text=_('Background image of a searcher tab. Both selected and not selected. (298x85)<br />You can use <a href="/media/img/searcher_tab_a_visits.gif" target="_blank">this image</a> as a template.'),
        )

    searcher_last_tab_image = models.ImageField(
        verbose_name= ('searcher last tab image'),
        upload_to='sections_styles',
        null=True,
        blank=True,
        help_text=_('Background image of the last searcher tab. Both selected and not selected. (299x85)<br />You can use <a href="/media/img/searcher_tab_b_visits.gif" target="_blank">this image</a> as a template.'),
        )

    search_results_item_background = models.ImageField(
        verbose_name= ('search results item background'),
        upload_to='sections_styles',
        null=True,
        blank=True,
        help_text=_('A vertical gradient image for use in the search results item backgrounds. (1x126)'),
        )

    menu_head_background = models.ImageField(
        verbose_name= ('menu head background'),
        upload_to='sections_styles',
        null=True,
        blank=True,
        help_text=_('Background image for headers in the menu zone. (175x34)'),
        )

    content_head_background = models.ImageField(
        verbose_name= ('content head background'),
        upload_to='sections_styles',
        null=True,
        blank=True,
        help_text=_('Background image for headers in the content zone. (775x34)'),
        )


def create_menus(sender, **kwargs):
    created = kwargs.get('created', False)
    instance = kwargs.get('instance')

    if created:
        instance.main_menu = Menu.objects.create(
                        name_es='Main menu of %s' % unicode(instance))
        instance.secondary_menu = Menu.objects.create(
                        name_es='Secondary menu of %s' % unicode(instance))
        instance.interest_menu = Menu.objects.create(
                        name_es='Interest menu of %s' % unicode(instance))
        instance.save()

post_save.connect(create_menus, sender=Section, dispatch_uid='SectionMenusSignalDispatcher')
post_save.connect(create_menus, sender=AppSection, dispatch_uid='AppSectionMenusSignalDispatcher')


def handle_link_url_post_save(sender, instance, **kwargs):
    linklist = []
    if isinstance(instance, BaseLink):
        linklist = [instance]
    elif isinstance(instance, BaseContent):
        try:
            linklist = [instance.contentlink]
        except ContentLink.DoesNotExist:
            pass
    elif isinstance(instance, BaseSection):
        for content in instance.related_content.all():
            try:
                linklist.append(content.contentlink)
            except ContentLink.DoesNotExist:
                continue

    for link in linklist:
        if link and link.get_absolute_url() != link.menu.url:
            link.menu.update_url()

post_save.connect(handle_link_url_post_save)
