# -*- coding: utf-8 -*-
import os
import re

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.db.models import signals, permalink
from django.db.models.query import delete_objects, CollectedObjects
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib.auth.models import User

from cmsutils.db.fields import AutoSlugField
from cmsutils.signals import post_rebuild_db
if settings.USE_GIS:
    from south.introspection_plugins import geodjango
from south.signals import pre_migrate, post_migrate
from stdimage import StdImageField
from transmeta import TransMeta
from tagging.fields import TagField

from merengue.base.managers import BaseContentManager, WorkflowManager
from merengue.multimedia.models import BaseMultimedia
from merengue.places.models import Location


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
    slug = AutoSlugField(verbose_name=_('slug'), autofromfield='name_es',
                         max_length=200, db_index=True, editable=False)

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
    plain_description = models.TextField(verbose_name=_('description'),
                                         null=True, blank=True, editable=False)
    description = models.TextField(verbose_name=_('description'),
                                   null=True, blank=True)

    status = models.CharField(_('Publication status'), max_length=20, choices=settings.STATUS_LIST,
                              default='draft', help_text=_('Enter the current status'), db_index=True,
                              editable=True)
    main_image = StdImageField(_('main image'), upload_to='content_images',
                               thumbnail_size=(200, 200),
                               null=True, blank=True, editable=True)

    objects = WorkflowManager()

    class Meta:
        abstract = True
        translate = ('name', 'description', 'plain_description', )
        ordering = ('name_es', )

    def __unicode__(self):
        return self.name or ugettext('Without name')

    def save(self, *args, **kwargs):
        for lang in settings.LANGUAGES:
            field_name = 'description_%s' % lang[0]
            to_field = 'plain_description_%s' % lang[0]

            original_text = getattr(self, field_name, None)
            if original_text:
                original_text = force_unicode(original_text)
                text = re.sub('<br[^>]*>', u'\n', original_text)
                text = unescape_entities(text)
                text = strip_tags(text)
                text = text.strip()
                setattr(self, to_field, text)
            else:
                setattr(self, to_field, original_text)
        super(Base, self).save(*args, **kwargs)

    @permalink
    def get_admin_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self)
        return ('merengue.base.views.admin_link', [content_type.id, self.id, ''])

    def is_published(self):
        return self.status == 'published'


BaseClass = Base
if settings.USE_GIS:
    from merengue.places.models import Location

    class LocatableContent(Base):
        """ Base class for all locatable content """
        # map icon for google maps
        map_icon = StdImageField(_('map icon'), upload_to='map_icons',
                                   null=True, blank=True)
        is_autolocated = models.BooleanField(verbose_name=_("is autolocated"),
                                          default=False)
        location = models.ForeignKey(Location, verbose_name=_('location'),
                                     null=True, blank=True, editable=False)

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
            return settings.MEDIA_URL + 'img/default_map_icon.jpg'

    def get_icon_tag(self):
        return '<img src="%s" title="%s"/>' %(self.get_icon(), self._meta.verbose_name)
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
    '''

    def __new__(cls, name, bases, attrs):
        if 'Meta' in attrs and hasattr(attrs['Meta'], 'content_view_template'):
            content_view_template = attrs['Meta'].content_view_template
            delattr(attrs['Meta'], 'content_view_template')
        else:
            content_view_template = 'content_view.html'

        new_class = super(BaseContentMeta, cls).__new__(cls, name, bases, attrs)
        if hasattr(new_class, '_meta'):
            new_class._meta.content_view_template = content_view_template
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

    last_editor = models.ForeignKey(User, null=True, blank=True, editable=False,
                                    related_name='last_edited_content')
    last_editor.delete_cascade=False

    # tagging info
    tags = TagField(verbose_name=_('Tags'))

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

    objects = BaseContentManager()

    class Meta:
        verbose_name = _('base content')
        verbose_name_plural = _('base contents')
        abstract = False
        permissions = (
            ("can_draft", "Can set as draft"),
            ("can_pending", "Can set as pending"),
            ("can_published", "Can set as published"),
            ("can_change_is_autolocated", "Can edit is_autolocated field"),
            ("can_change_main_image", "Can edit main image field"),
            ("can_change_map_icon", "Can edit map icon field"),
        )
        ordering = ('name_es', )
        #content_view_template = 'content_view.html' # default definition by BaseContentMeta metaclass

    @classmethod
    def get_menu_name(cls):
        return u"%s_menu" % cls._meta.module_name

    def save(self, update_rank=True, **kwargs):
        super(BaseContent, self).save(**kwargs)
        object_update_again = False

        if update_rank:
            self.rank = self.calculate_rank()
            object_update_again = True

        tags_field = self._meta.get_field('tags')
        tags_field._save(instance=self)

        # Save thumbnail of main_image in model inherited
        main_image_field = self._meta.get_field('main_image')
        try:
            main_image_field._rename_resize_image(instance=self)
        except OSError:
            pass # this may fail if the image file does not exist

        if object_update_again:
            non_pks = [f for f in self._meta.local_fields if not f.primary_key]
            if non_pks:
                # we force an update since we already did an insert
                super(BaseContent, self).save(force_update=True)

    def get_real_instance(self):
        """ get object child instance """
        if hasattr(self, '_real_instance'): # try looking in our cache
            return self._real_instance
        real_instance = getattr(self, self.class_name, self)
        self._real_instance = real_instance
        return real_instance

    @permalink
    def get_absolute_url(self):
        return ('merengue.base.views.public_link', [self._meta.app_label, self._meta.module_name, self.id])

    @permalink
    def public_link(self):
        section = self.get_main_section()
        if section:
            return ('content_section_view', [section.slug, self.id, self.slug])
        else:
            return ('merengue.base.views.public_view', [self._meta.app_label, self._meta.module_name, self.id, self.slug])

    def link_by_user(self, user):
        """ User dependent link. To override in subclasses, if needed """
        raise NotImplementedError("Model %s has no implements a link_by_user method" % self._meta)

    def can_edit(self, user):
        if not user.is_authenticated():
            return False
        if user.is_superuser or (user.is_staff and \
           user.has_perm(self._meta.app_label + '.' + self._meta.get_change_permission())):
            return True
        return not self.is_published() and user in self.owners.all()

    def get_icon(self):
        if self.map_icon:
            return super(BaseContent, self).get_icon()
        else:
            return settings.MEDIA_URL + 'img/' + self.get_class_name() + '_map_icon.jpg'

    def get_main_section(self):
        """ Get main section of a content """
        try:
            return self.basesection_set.main()
        except ObjectDoesNotExist:
            return None

    def calculate_rank(self):
        return 100.0 # default implementation

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


def calculate_class_name(instance):
    instance.class_name = instance._meta.module_name


def base_content_pre_save_handler(sender, instance, **kwargs):
    if isinstance(instance, BaseContent) and not instance.id:
        calculate_class_name(instance)


signals.pre_save.connect(base_content_pre_save_handler)


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
            return self.order+1
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
                                                  order=self.order+1)
            return next
        except MultimediaRelation.DoesNotExist:
            return self

    def get_previous_multimedia(self):
        try:
            previous = MultimediaRelation.objects.get(content=self.content,
                                                      order=self.order-1)
            return previous
        except MultimediaRelation.DoesNotExist:
            return self

    def set_as_main_image(self):
        if self.class_name == 'photo':
            self.content.main_image.save(os.path.basename(self.multimedia.photo.image.name),
                                         self.multimedia.photo.image)
            self.content.save()


def ensure_break_relations(sender, instance, **kwargs):
    if hasattr(instance, 'break_relations'):
        instance.break_relations()

signals.pre_delete.connect(ensure_break_relations)


def init_gis(sender, **kwargs):
    call_command('init_gis')


def recalculate_main_image(sender, instance, **kwargs):
    """ recalculate main_image after deleting a relation """
    if instance.multimedia.class_name == 'photo' and instance.order == 0:
        ordered_photo_relations = MultimediaRelation.objects.filter(
            multimedia__class_name='photo',
            content=instance.content,
        ).order_by('order')
        # we can assert instance will not be in ordered_photo_relations
        if ordered_photo_relations:
            # reorder photos
            for i, mr in enumerate(ordered_photo_relations):
                mr.order = i
                mr.save()
        instance.content.recalculate_main_image()


signals.post_delete.connect(recalculate_main_image, sender=MultimediaRelation)
post_rebuild_db.connect(init_gis)


def _collect_sub_objects(self, seen_objs, parent=None, nullable=False):
    """
    Recursively populates seen_objs with all objects related to this
    object.

    When done, seen_objs.items() will be in the format:
        [(model_class, {pk_val: obj, pk_val: obj, ...}),
         (model_class, {pk_val: obj, pk_val: obj, ...}), ...]
    """
    pk_val = self._get_pk_val()
    if seen_objs.add(self.__class__, pk_val, self, parent, nullable):
        return

    for related in self._meta.get_all_related_objects():
        rel_opts_name = related.get_accessor_name()
        field = related.field
        delete_cascade = getattr(field, 'delete_cascade', True)
        if not delete_cascade:
            continue
        if isinstance(related.field.rel, models.OneToOneRel):
            try:
                sub_obj = getattr(self, rel_opts_name)
            except ObjectDoesNotExist:
                pass
            else:
                sub_obj._collect_sub_objects(seen_objs, self.__class__, related.field.null)
        else:
            for sub_obj in getattr(self, rel_opts_name).all():
                sub_obj._collect_sub_objects(seen_objs, self.__class__, related.field.null)

    # Handle any ancestors (for the model-inheritance case). We do this by
    # traversing to the most remote parent classes -- those with no parents
    # themselves -- and then adding those instances to the collection. That
    # will include all the child instances down to "self".
    parent_stack = self._meta.parents.values()
    while parent_stack:
        link = parent_stack.pop()
        parent_obj = getattr(self, link.name)
        if parent_obj._meta.parents:
            parent_stack.extend(parent_obj._meta.parents.values())
            continue
        # At this point, parent_obj is base class (no ancestor models). So
        # delete it and all its descendents.
        parent_obj._collect_sub_objects(seen_objs)


def break_relations(self):
    for related in self._meta.get_all_related_objects():
        rel_opts_name = related.get_accessor_name()
        field = related.field
        delete_cascade = getattr(field, 'delete_cascade', True)
        if not delete_cascade:
            if isinstance(related.field.rel, models.OneToOneRel):
                setattr(self, rel_opts_name, None)
            else:
                for sub_obj in getattr(self, rel_opts_name).all():
                    setattr(sub_obj, related.field.name, None)
                    sub_obj.save()


def delete(self):
    assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)

    # Break relations
    self.break_relations()

    # Find all the objects than need to be deleted.
    seen_objs = CollectedObjects()
    self._collect_sub_objects(seen_objs)

    # Actually delete the objects.
    delete_objects(seen_objs)

delete.alters_data = True

models.Model.add_to_class('delete', delete)
models.Model.add_to_class('break_relations', break_relations)
models.Model.add_to_class('_collect_sub_objects', _collect_sub_objects)


# ----- south signals handling -----

post_save_receivers = None


def handle_pre_migrate(sender, **kwargs):
    global post_save_receivers
    post_save_receivers = post_save.receivers
    post_save.receivers = []


def handle_post_migrate(sender, **kwargs):
    global post_save_receivers
    post_save.receivers = post_save_receivers


pre_migrate.connect(handle_pre_migrate)
post_migrate.connect(handle_post_migrate)
