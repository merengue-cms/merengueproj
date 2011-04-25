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

# -*- coding: utf-8 -*-
import os
import re

from django.conf import settings
if settings.USE_GIS:
    from django.contrib.gis.db import models
else:
    from django.db import models  # pyflakes:ignore
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation, ValidationError
from django.db.models import signals, permalink
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from cmsutils.signals import post_rebuild_db
if settings.USE_GIS:
    from south.introspection_plugins import geodjango  # pyflakes:ignore
from south.modelsinspector import add_introspection_rules
from south.signals import pre_migrate, post_migrate
from stdimage import StdImageField
from transmeta import TransMeta, get_fallback_fieldname
from tagging.models import Tag
from tagging.fields import TagField

from merengue.base.dbfields import AutoSlugField, JSONField
from merengue.base.managers import BaseContentManager, WorkflowManager
from merengue.base.review_tasks import review_to_pending_status
from merengue.urlresolvers import get_url_default_lang
from merengue.multimedia.models import BaseMultimedia
from merengue.utils import is_last_application
from merengue.workflow.models import State


PRIORITY_CHOICES = (
    (1, _('Lowest')),
    (2, _('Very Low')),
    (3, _('Low')),
    (4, _('Medium')),
    (5, _('High')),
    (6, _('Very high')),
    (7, _('Super high')),
    (8, _('Highest')),
    )


COMMENTABLE_CHOICES = (
    ('disabled', _('disabled')),
    ('allowed', _('allowed')),
    )


class ContactInfo(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=200,
                            blank=True, null=True)
    contact_email = models.EmailField(verbose_name=_('contact email'),
                                     max_length=200, blank=True, null=True)
    contact_email2 = models.EmailField(verbose_name=_('contact email2'),
                                      max_length=200, blank=True, null=True)
    url = models.CharField(verbose_name=_('url'), max_length=200,
                           blank=True, null=True)
    phone = models.CharField(verbose_name=_('phone'), max_length=200,
                             blank=True, null=True)
    phone2 = models.CharField(verbose_name=_('phone2'), max_length=200,
                              blank=True, null=True)
    fax = models.CharField(verbose_name=_('fax'), max_length=200,
                           blank=True, null=True)

    class Meta:
        verbose_name = _('contact info')
        verbose_name_plural = _('contacts info')

    def __unicode__(self):
        return self.contact_email or ugettext('Without contact email')


class BaseCategory(models.Model):
    __metaclass__ = TransMeta
    name = models.CharField(verbose_name=_('name'), max_length=200)
    slug = models.SlugField(verbose_name=_('slug'), max_length=200, db_index=True)

    class Meta:
        verbose_name = _('base category')
        verbose_name_plural = _('base categories')
        abstract = True
        translate = ('name', )

    def __unicode__(self):
        return self.name

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self)
        return ('merengue.base.views.admin_link', [content_type.id, self.id, ''])


class Base(models.Model):
    __metaclass__ = TransMeta
    name = models.CharField(verbose_name=_('name'), max_length=200, db_index=True)
    slug = models.SlugField(verbose_name=_('slug'), max_length=200, db_index=True, unique=True)
    plain_description = models.TextField(verbose_name=_('plain text description'),
                                         null=True, blank=True, editable=False)
    description = models.TextField(verbose_name=_('description'),
                                   null=True, blank=True)

    status = models.CharField(_('Publication status'), max_length=20, choices=settings.STATUS_LIST,
                              default='draft', help_text=_('Enter the current status'), db_index=True,
                              editable=True)
    workflow_status = models.ForeignKey(State, verbose_name=_('workflow status'),
                                       null=True, blank=True, editable=True)
    main_image = StdImageField(_('main image'), upload_to='content_images',
                               thumbnail_size=(200, 200),
                               null=True, blank=True, editable=False)

    objects = WorkflowManager()

    class Meta:
        abstract = True
        translate = ('name', 'description', 'plain_description', )
        ordering = (get_fallback_fieldname('name'), )

    def __unicode__(self):
        return self.name or ugettext('Without name')

    def _prepare_plain_text(self, from_field, to_field):
        original_text = getattr(self, from_field, None)
        if original_text:
            original_text = force_unicode(original_text)
            text = re.sub('<br[^>]*>', u'\n', original_text)
            text = unescape_entities(text)
            text = strip_tags(text)
            text = text.strip()
            setattr(self, to_field, text)
        else:
            setattr(self, to_field, original_text)

    def clean(self):
        super(Base, self).clean()
        # avoid integer overflows
        numeric_fields = [models.IntegerField, models.PositiveIntegerField,
                          models.PositiveSmallIntegerField, models.SmallIntegerField]
        invalid_fields = set()
        for field in self._meta.fields:
            for numeric in numeric_fields:
                if isinstance(field, numeric) and field.value_from_object(self) > settings.MAX_INT_VALUE:
                    invalid_fields.add(field)
                    continue
        if invalid_fields:
            error_msg = u"%s: %s %d" % (', '.join([force_unicode(f.verbose_name) for f in invalid_fields]),
                                        _('Numeric fields can not be larger than'),
                                        settings.MAX_INT_VALUE)
            raise ValidationError(error_msg)

    def get_status_object(self):
        # since the connection with the state is created on the post-save
        # signal, it will allways exists.
        return self.stateobjectrelation_set.all()[0].state

    def save(self, *args, **kwargs):
        for lang in settings.LANGUAGES:
            field_name = 'description_%s' % lang[0]
            to_field = 'plain_description_%s' % lang[0]
            self._prepare_plain_text(field_name, to_field)

        super(Base, self).save(*args, **kwargs)

    def update_status(self):
        """We assume that State is changed
        """
        from merengue.perms.models import ObjectPermission
        self.status = self.workflow_status.slug
        if hasattr(self, 'objectpermission_set'):
            self.objectpermission_set.all().delete()
            for perm in self.workflow_status.statepermissionrelation_set.all():
                self.objectpermission_set.add(
                    ObjectPermission.objects.create(content=self,
                                                    role=perm.role,
                                                    permission=perm.permission))
        self.save()

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self)
        return ('merengue.base.views.admin_link', [content_type.id, self.id, ''])

    def is_published(self):
        return self.status == 'published'


def base_post_save_handler(sender, instance, created, **kwargs):
    if 'status' in instance.__dict__ and hasattr(instance, 'workflow_status') and instance.status != instance.workflow_status.slug:
        instance.update_status()


signals.post_save.connect(base_post_save_handler)


BaseClass = Base
if settings.USE_GIS:
    from merengue.places.models import Location

    class LocatableContent(Base):
        """ Base class for all locatable content """
        # map icon for google maps
        map_icon = StdImageField(_('map icon'), upload_to='map_icons',
                                   null=True, blank=True)
        location = models.ForeignKey(Location, verbose_name=_('location'),
                                     null=True, blank=True, editable=False,
                                     on_delete=models.SET_NULL)
        location.delete_cascade = False

        objects = WorkflowManager()

        class Meta:
            abstract = True

        @property
        def main_location(self):
            if self.location is not None:
                return self.location.main_location
            return None

        def get_icon(self):
            if self.map_icon:
                return self.map_icon.url
            else:
                return settings.MEDIA_URL + 'merengue/img/map/default_map_icon.png'

        def get_icon_tag(self):
            return '<img src="%s" title="%s"/>' % (self.get_icon(), self._meta.verbose_name)
        get_icon_tag.allow_tags = True

        def has_location(self):
            return self.location and self.location.has_location()

        def google_minimap(self):
            location = self.main_location
            if location:
                return render_to_string('admin/mini_google_map.html',
                                        {'content': self,
                                         'zoom': 16,
                                         'index': self.id,
                                         'MEDIA_URL': settings.MEDIA_URL,
                                         'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})
            else:
                return _('Without location')
        google_minimap.allow_tags = True

        def admin_thumbnail(self):
            #@FIXME: Duplicate code. multimedia/models.py line 205
            if not self.main_image:
                return ''
            file_access_failed = False
            try:
                if not self.main_image or not self.main_image.thumbnail or \
                   not os.path.exists(self.main_image.thumbnail.path()):
                    file_access_failed = True
            except SuspiciousOperation:
                file_access_failed = True

            if file_access_failed:
                # in development server may not exists thumbnails from
                # production db. See ticket #1659
                return 'file not exists in filesystem'

            thumb_url = self.main_image.thumbnail.url()
            return u'<a href="%s"><img src="%s" alt="%s" /></a>' % \
                        (self.main_image.url, thumb_url, self.name)
        admin_thumbnail.short_description = _('Thumbnail')
        admin_thumbnail.allow_tags = True

    BaseClass = LocatableContent


class BaseContentMeta(TransMeta):
    '''
    Metaclass for all base content types.

    The syntax to us it is next:

        class MyModel(BaseContent):
            my_field = models.CharField(max_length=20)

            class Meta:
                content_view_template = 'myapp/mymodel_view.html'
                content_view_function = 'myapp.mymodel_view'
    '''

    def __new__(cls, name, bases, attrs):
        if 'Meta' in attrs and hasattr(attrs['Meta'], 'content_view_template'):
            content_view_template = attrs['Meta'].content_view_template
            delattr(attrs['Meta'], 'content_view_template')
        else:
            content_view_template = 'content_view.html'
        if 'Meta' in attrs and hasattr(attrs['Meta'], 'content_view_function'):
            content_view_function = attrs['Meta'].content_view_function
            delattr(attrs['Meta'], 'content_view_function')
        else:
            content_view_function = None

        new_class = super(BaseContentMeta, cls).__new__(cls, name, bases, attrs)
        if hasattr(new_class, '_meta'):
            new_class._meta.content_view_template = content_view_template
            new_class._meta.content_view_function = content_view_function
        return new_class


class BaseContent(BaseClass):
    __metaclass__ = BaseContentMeta

    contact_info = models.ForeignKey(ContactInfo,
                                     verbose_name=_('contact info'),
                                     null=True, blank=True, editable=False)
    related_items = models.ManyToManyField('BaseContent',
                                           verbose_name=_('related items'),
                                           null=True, blank=True, editable=False)
    creation_date = models.DateTimeField(verbose_name=_('creation date'),
                                         blank=True, null=True, auto_now_add=True)

    modification_date = models.DateTimeField(verbose_name=_('modification date'),
                                             blank=True, null=True, auto_now=True)

    # this is handled in admin forms
    user_modification_date = models.DateTimeField(verbose_name=_('modification date'),
                                                  blank=True, null=True, editable=False)
    cached_plain_text = models.TextField(verbose_name=_('cached plain text'),
                                   null=True, blank=True, editable=False)

    last_editor = models.ForeignKey(User, null=True, blank=True, editable=False,
                                    related_name='last_edited_content',
                                    on_delete=models.SET_NULL)

    # permission global
    adquire_global_permissions = models.BooleanField(_('Adquire global permissions'), default=False)

    # tagging info
    tags = TagField(verbose_name=_('Tags'),
                    help_text=_('Tags will be splitted by spaces or commas if present. To force \
                                tag names, use double quotes.'))

    # meta info
    meta_desc = models.TextField(verbose_name=_('meta description'), null=True, blank=True)

    commentable = models.CharField(_('comments'), max_length=20, choices=COMMENTABLE_CHOICES,
                              default='allowed', help_text=_('Is that content commentable'),
                              editable=True)

    # multimedia resources
    multimedia = models.ManyToManyField(BaseMultimedia,
                                        verbose_name=_('multimedia'),
                                        through='MultimediaRelation',
                                        blank=True)

    # cached class name from this content
    # this should has null=False, blank=False but in practice this
    # is not possible due to the way the class_name is computed
    # (the object need to get its child class and this is not
    # available until the parent register is saved)
    class_name = models.CharField(verbose_name=_('class name'),
                                  max_length=100, db_index=True,
                                  editable=False, null=True)

    # ranking system
    rank = models.FloatField(verbose_name=_('rank value'),
                             default=100.0, db_index=True,
                             editable=False, blank=False)

    # access control
    owners = models.ManyToManyField(User,
                                    verbose_name=_('owners'),
                                    null=True, blank=True,
                                    related_name='contents_owned')

    position = models.PositiveIntegerField(verbose_name=_('position'),
                                           null=True,
                                           editable=False)

    # structural contents
    no_changeable = models.BooleanField(default=False,
                                        editable=False)
    no_deletable = models.BooleanField(default=False,
                                       editable=False)

    # block control. cached value for controlling if content has special blocks attached
    has_related_blocks = models.BooleanField(default=False, editable=False,
                                             db_index=True)

    # structural fields
    no_changeable_fields = JSONField(null=True, blank=True,
                                     editable=False)

    objects = BaseContentManager()

    def __init__(self, *args, **kwargs):
        super(BaseContent, self).__init__(*args, **kwargs)
        self._original_status = self.status

    def generate_plain_text(self):
        return strip_tags(self.description)

    def _plain_text(self):
        if not self.cached_plain_text:
            for lang in settings.LANGUAGES:
                from_field = 'description_%s' % lang[0]
                to_field = 'cached_plain_text_%s' % lang[0]
                self._prepare_plain_text(from_field, to_field)
            self.save()
        return self.cached_plain_text

    plain_text = property(_plain_text)

    class Meta:
        verbose_name = _('base content')
        verbose_name_plural = _('base contents')
        translate = ('cached_plain_text', )
        abstract = False
        #content_view_template = 'content_view.html' # default definition by BaseContentMeta metaclass
        ordering = ('position', get_fallback_fieldname('name'), )

    def admin_absolute_url(self):
        return '<a href="%s">%s</a>' % (self.get_real_instance().get_admin_absolute_url(), self.name)
    admin_absolute_url.allow_tags = True

    @classmethod
    def get_menu_name(cls):
        return u"%s_menu" % cls._meta.module_name

    def save(self, update_rank=True, **kwargs):
        # new objects should be added in last place
        if not self.id:
            try:
                ordered = self.__class__.objects.filter(position__isnull=False).order_by('-position')
                last = ordered[0]
                self.position = last.position + 1
            except IndexError:
                pass

        super(BaseContent, self).save(**kwargs)
        object_update_again = False

        if update_rank:
            self.rank = self.calculate_rank()
            object_update_again = True

        tags_field = self._meta.get_field('tags')
        tags_field._save(instance=self)
        # updating the tags may leave some without related items, so we'll delete them
        for tag in Tag.objects.filter(items__isnull=True):
            if hasattr(tag, 'itag'):
                # itag deletion gets rid of the original tag object
                tag.itag.delete()
            else:
                tag.delete()

        # Save thumbnail of main_image in model inherited
        main_image_field = self._meta.get_field('main_image')
        try:
            main_image_field._rename_resize_image(instance=self)
        except OSError:
            pass  # this may fail if the image file does not exist

        if object_update_again:
            non_pks = [f for f in self._meta.local_fields if not f.primary_key]
            if non_pks:
                # we force an update since we already did an insert
                super(BaseContent, self).save(force_update=True)

    def get_real_instance(self):
        """ get object child instance """
        def get_subclasses(cls):
            subclasses = cls.__subclasses__()
            result = []
            for subclass in subclasses:
                if not subclass._meta.abstract:
                    result.append(subclass)
                else:
                    result += get_subclasses(subclass)
            return result

        if hasattr(self, '_real_instance'):  # try looking in our cache
            return self._real_instance
        subclasses = get_subclasses(self.__class__)
        if not subclasses:  # already real_instance
            real_instance = getattr(self, self.class_name, self)
            self._real_instance = real_instance
            return real_instance
        else:
            subclasses_names = [cls.__name__.lower() for cls in subclasses]
            for subcls_name in subclasses_names:
                if hasattr(self, subcls_name):
                    return getattr(self, subcls_name, self).get_real_instance()
            return self

    @permalink
    def get_absolute_url(self):
        return ('merengue.base.views.public_link', [self._meta.app_label, self._meta.module_name, self.id])

    @permalink
    def public_link_without_section(self):
        return self._public_link_without_section()

    def _public_link_without_section(self):
        return ('merengue.base.views.public_view', [self._meta.app_label, self._meta.module_name, self.id, self.slug])

    @permalink
    def public_link(self):
        section = self.get_main_section()
        if section:
            return section.get_real_instance()._content_public_link(section, self)
        else:
            return self._public_link_without_section()

    def link_by_user(self, user):
        """ User dependent link. To override in subclasses, if needed """
        raise NotImplementedError("Model %s has no implements a link_by_user method" % self._meta)

    def can_edit(self, user):
        from merengue.perms.utils import has_permission
        return has_permission(self, user, 'edit')

    def get_main_section(self):
        """ Get main section of a content """
        try:
            return self.sections.main()
        except ObjectDoesNotExist:
            return None

    def calculate_rank(self):
        return 100.0  # default implementation

    def recalculate_main_image(self):
        """ main image will be first ordered multimedia relation with class "photo" """
        ordered_photo_relations = MultimediaRelation.objects.filter(
            multimedia__class_name='photo',
            content=self,
        ).order_by('order')
        if ordered_photo_relations:
            first_photo = ordered_photo_relations[0].multimedia.get_real_instance()
            if os.path.exists(first_photo.image.path):
                self.main_image.save(os.path.basename(first_photo.image.name),
                                     first_photo.image)
                self.save()
        elif self.main_image:
            # we delete photo if not exists ordered photos for this content
            self.main_image.delete()

    @classmethod
    def get_resource_order(cls):
        return cls._meta.ordering

    def is_commentable(self):
        return self.commentable == 'allowed'

    def breadcrumbs_first_item(self):
        from merengue.pluggable.utils import get_plugin_config
        plugin_dir = self._meta.app_label
        plugin_config = get_plugin_config(plugin_dir)
        if plugin_config is None:
            return None  # item model is outside plugin... no first item generated
        url_prefix = plugin_config.url_prefixes[0][0]
        if isinstance(url_prefix, dict):
            url_prefix = url_prefix.get(get_url_default_lang(), 'en')
        plugin_url = "/%s/" % url_prefix
        return (self._meta.verbose_name_plural, plugin_url)

    def breadcrumbs_last_item(self):
        return (unicode(self), '')

    def breadcrumbs_items(self):
        urls = []
        try:
            first_item = self.breadcrumbs_first_item()
            if first_item:
                urls.append(first_item)
        except ImportError:
            urls = []
        last_item = self.breadcrumbs_last_item()
        if last_item:
            urls.append(last_item)
        return urls

    def breadcrumbs(self):
        urls = self.breadcrumbs_items()
        return render_to_string('base/breadcrumbs.html', {'urls': urls})

    def update_status(self):
        """We assume that State is changed
        """
        super(BaseContent, self).update_status()
        from merengue.perms.models import ObjectPermission
        self.objectpermission_set.all().delete()
        for perm in self.workflow_status.statepermissionrelation_set.all():
            self.objectpermission_set.add(
                ObjectPermission.objects.create(content=self,
                                                role=perm.role,
                                                permission=perm.permission))
        self.save()


def calculate_class_name(instance):
    instance.class_name = instance._meta.module_name


def base_content_pre_save_handler(sender, instance, **kwargs):
    if isinstance(instance, BaseContent) and not instance.id:
        calculate_class_name(instance)


signals.pre_save.connect(base_content_pre_save_handler)


def notify_status_changes(sender, instance, **kwargs):
    if isinstance(instance, BaseContent):
        if not hasattr(instance, '_original_status'):
            return
        if instance._original_status == instance.status:
            return
        if instance.status == 'pending':
            review_to_pending_status(instance, instance._original_status)
        # Change cached original status so if we have
        # multiple saves we don't generate multiple
        # review tasks
        instance._original_status = instance.status

signals.post_save.connect(notify_status_changes)


class MultimediaRelation(models.Model):
    content = models.ForeignKey(BaseContent, verbose_name=_('content'))
    multimedia = models.ForeignKey(BaseMultimedia,
                                  verbose_name=_("multimedia"),
                                  )
    is_featured = models.BooleanField(verbose_name=_("is featured"),
                                      default=False)
    # The order goes from 0 to n - 1
    order = models.IntegerField(_("Order"), blank=True, null=True)

    class Meta:
        ordering = ('order', )
        verbose_name = _("multimedia relation")
        verbose_name_plural = _("multimedia relations")
        unique_together = ('content', 'multimedia')

    def __unicode__(self):
        return unicode(self.content)

    def save(self, update_order=False, **kwargs):
        if self.id is None:
            update_order = True
        super(MultimediaRelation, self).save(**kwargs)
        if update_order:
            self.order = self._get_next_order()
            self.save()
        if self.multimedia.class_name == 'photo' and self.order == 0:
            self.content.recalculate_main_image()

    def get_image(self):
        instance = self.multimedia.get_real_instance()
        image = getattr(instance, 'image', None) or \
                getattr(instance, 'preview', None)
        return image

    def _get_human_order(self):
        if self.order != None:
            return self.order + 1
        return ''
    _get_human_order.short_description = _('Human Order')
    human_order = property(_get_human_order)

    def _get_next_order(self):
        order = 0
        order_query_set = MultimediaRelation.objects.filter(
                            content=self.content,
                            multimedia__class_name=self.multimedia.class_name,
                            order__isnull=False).order_by('-order')
        if order_query_set:
            last = order_query_set[0].order
            if last is not None:
                order = last + 1
        return order

    def get_next_multimedia(self):
        try:
            next = MultimediaRelation.objects.get(content=self.content,
                                                  order=self.order + 1)
            return next
        except MultimediaRelation.DoesNotExist:
            return self

    def get_previous_multimedia(self):
        try:
            previous = MultimediaRelation.objects.get(content=self.content,
                                                      order=self.order - 1)
            return previous
        except MultimediaRelation.DoesNotExist:
            return self

    def set_as_main_image(self):
        if self.class_name == 'photo':
            self.content.main_image.save(os.path.basename(self.multimedia.photo.image.name),
                                         self.multimedia.photo.image)
            self.content.save()


def init_gis(sender, **kwargs):
    call_command('init_gis')


def recalculate_main_image(sender, instance, **kwargs):
    """ recalculate main_image after deleting a relation """
    if instance.multimedia.class_name == 'photo' and instance.order == 0:
        ordered_photo_relations = MultimediaRelation.objects.filter(
            multimedia__class_name='photo',
            content=instance.content,
        ).exclude(pk=instance.pk).order_by('order')
        # we can assert instance will not be in ordered_photo_relations
        if ordered_photo_relations:
            # reorder photos
            for i, mr in enumerate(ordered_photo_relations):
                mr.order = i
                mr.save()
            instance.content.recalculate_main_image()
        elif instance.content.main_image:
            instance.content.main_image.delete()


signals.pre_delete.connect(recalculate_main_image, sender=MultimediaRelation)
if settings.USE_GIS:
    post_rebuild_db.connect(init_gis)


# ----- adding south rules to help introspection -----

rules = [
  (
    (AutoSlugField, ),
    [],
    {"autofromfield": ["autofromfield", {}]},
  ),
]

add_introspection_rules(rules, ["^cmsutils\.db\.fields\.AutoSlugField"])

# ----- south signals handling -----

post_save_receivers = None
cache_backend = None


def handle_pre_migrate(sender, **kwargs):
    global post_save_receivers, cache_backend
    # remove post save receivers because we cannot to call create_menus signal
    post_save_receivers = post_save.receivers
    post_save.receivers = []
    # use dummy cache backend because Johnny cache does weird things. See #852
    cache_backend = settings.CACHES['default']['BACKEND']
    settings.CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'


def handle_post_migrate(sender, **kwargs):
    from merengue.pluggable import enable_active_plugins
    global post_save_receivers, cache_backend
    app = kwargs['app']
    if is_last_application(app):
        enable_active_plugins()
    # site fixtures loading after migration
    for app_name, fixtures in getattr(settings, 'SITE_FIXTURES', {}).items():
        if app_name == app:  # only migrate
            for fixture in fixtures:
                call_command('loaddata', fixture, verbosity=1)
    # will set again saved receivers and cache backend
    post_save.receivers = post_save_receivers
    settings.CACHES['default']['BACKEND'] = cache_backend


pre_migrate.connect(handle_pre_migrate)
post_migrate.connect(handle_post_migrate)
