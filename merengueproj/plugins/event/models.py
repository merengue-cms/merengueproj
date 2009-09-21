import datetime

from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import permalink
from django.db.models.signals import post_save, post_delete
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from transmeta import TransMeta

from merengue.base.models import BaseContent, BaseCategory, ContactInfo
from merengue.section.models import BaseSection
from merengue.places.models import Location

from plugins.event.managers import EventManager, OccurrenceManager


FREQS = (("YEARLY", _("Yearly")),
         ("MONTHLY", _("Monthly")),
        )


class CategoryGroup(BaseCategory):
    """ Event category group (deporte, playa, cultura, conciertos...) """
    sections = models.ManyToManyField(BaseSection,
                                      verbose_name=_('sections'),
                                      blank=True, null=True)
    hidden_in_global_search = models.BooleanField(verbose_name=_('hidden in global search'),
                                                  default=False)

    class Meta:
        verbose_name = _('category group')
        verbose_name_plural = _('category groups')


class Category(BaseCategory):
    """ Event category (deportes nauticos, toros, flamenco...) """
    sections = models.ManyToManyField(BaseSection,
                                      verbose_name=_('sections'),
                                      blank=True, null=True)
    groups = models.ManyToManyField(CategoryGroup,
                                    verbose_name=_('category groups'),
                                    blank=True, null=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')


class Event(BaseContent):
    """ Andalucia event """

    publish_date = models.DateTimeField(blank=True, null=True, db_index=True, editable=False)
    expire_date = models.DateTimeField(blank=True, null=True, db_index=True)
    cached_min_start = models.DateTimeField(_('Start date'), null=True, editable=False, db_index=True)
    cached_max_end = models.DateTimeField(_('End date'), null=True, editable=False, db_index=True)

    parent = models.ForeignKey('Event', verbose_name=_('parent event'),
                               null=True, blank=True)

    categories = models.ManyToManyField(Category,
                                      verbose_name=_('category'),
                                      blank=True, null=True, db_index=True)

    is_global = models.BooleanField(verbose_name=_('is global'),
                                    help_text=_('visible on all Andalusia places'),
                                    blank=True, default=False, db_index=True)

    is_highlight = models.BooleanField(verbose_name=_('is highlighted'),
                                       help_text=_('visible in agenda header'),
                                       blank=True, default=False, db_index=True)

    frequency = models.CharField(_("frequency"), choices=FREQS, max_length=10,
                                 blank=True, null=True)

    def _start(self):
        return self.cached_min_start
    start = property(_start)

    def _end(self):
        return self.cached_max_end
    end = property(_end)

    def _title(self):
        return self.name
    title = property(_title)

    objects = EventManager()

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')

    @permalink
    def public_link(self):
        return ('plugins.event.views.event_view', [self.slug])

    def __unicode__(self):
        return self.title or self.name or u''

    def get_locations(self):
        """ Get visible locations for maps """
        return [occurrence.main_location for occurrence in self.occurrence_event.visibles()]

    def update_location(self):
        if self.location is None:
            self.location = Location.objects.create()
        # XXX: see if this method is needed
        self.location.save()
        self.save()

    def has_location(self):
        return bool(self.main_location)

    def _main_location(self):
        if self.location is not None and self.location.main_location is not None:
            return self.location.main_location
        occurrence_locations = self.get_locations()
        for l in occurrence_locations:
            if l:
                return l
        return None
    main_location = property(_main_location)

    def get_location(self):
        if self.location is not None and self.location.main_location is not None:
            return self.location
        for occurrence in self.occurrence_event.visibles():
            if occurrence.main_location:
                return occurrence.location
        return None

    @classmethod
    def get_resource_order(cls):
        return ('cached_min_start', )

    def google_minimap(self):
        ocurrences = self.occurrence_event.published()
        if ocurrences:
            ocurrence = ocurrences[0]
            location = ocurrence.main_location
            if location:
                return render_to_string('admin/mini_google_map.html',
                                        {'content': ocurrence,
                                         'zoom': 16,
                                         'index': self.id,
                                         'MEDIA_URL': settings.MEDIA_URL,
                                         'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})
        return _('Without location')
    google_minimap.allow_tags = True


class Occurrence(models.Model):
    """ Event that occurs """
    __metaclass__ = TransMeta

    location = models.ForeignKey(Location, verbose_name=_('location'),
                                 null=True, blank=True, editable=False)

    place = models.CharField(_("name location"), max_length=200,
                                 blank=True, null=True)

    basecontent_location = models.ForeignKey(BaseContent,
                                             verbose_name=_('located in'),
                                             null=True, blank=True,
                                             editable=False)
    contact_info = models.ForeignKey(ContactInfo,
                                     verbose_name=_('contact info'),
                                     null=True, blank=True, editable=False)
    event = models.ForeignKey(Event,
                              verbose_name=_('event'),
                              related_name='occurrence_event')

    price = models.TextField(verbose_name=_('price'),
                            null=True, blank=True)

    schedule = models.TextField(verbose_name=_('schedule'),
                                null=True, blank=True)
    start = models.DateTimeField(null=True, verbose_name=_('start'))
    end = models.DateTimeField(null=True, verbose_name=_('end'))

    objects = OccurrenceManager()

    def _title(self):
        return unicode(self.event)

    title = property(_title)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('occurrence')
        verbose_name_plural = _('occurrences')
        translate = ('schedule', 'price', )
        ordering = ('start', )

    def get_icon(self):
        if self.event:
            return self.event.get_icon()
        else:
            return settings.MEDIA_URL + 'img/event_map_icon.jpg'

    def _main_location(self):
        # Si hay un contenido relacionado su localizacion es la que prevalece
        if self.basecontent_location is not None:
            return self.basecontent_location.main_location
        elif self.location is not None:
            return self.location.main_location
        return None
    main_location = property(_main_location)

    def has_location(self):
        return self.get_location() and self.get_location().has_location()

    def get_location(self):
        # Si hay un contenido relacionado su localizacion es la que prevalece
        if self.basecontent_location is not None:
            return self.basecontent_location.location
        elif self.location is not None:
            return self.location
        return None

    def has_been_located_in(self):
        if self.basecontent_location is not None:
            return True
        else:
            return False

    def get_admin_absolute_url(self):
        return '%sadmin/event/occurrence/%s/' % (self.event.get_admin_absolute_url(), self.id)

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

    def get_place(self):
        if self.place:
            return mark_safe("<span class='title'>%s</span>" %(self.place))
        else:
            locations = self.location.cities.all()
            if locations:
                location = locations[0]
                return mark_safe("<a href='%s'>%s</a>" %(location.get_absolute_url(), location))
        return ''

    def visible(self):
        return self.end > datetime.datetime.now()


def handle_event_post_save(sender, instance, created, **kwargs):
    """ Create first occurrence on after event is created """
    if created:
        occurrence = Occurrence()
        occurrence.event = instance
        occurrence.save()


post_save.connect(handle_event_post_save, sender=Event)


def update_event_cached_values(sender, instance, **kwargs):
    event = instance.event
    need_to_save = False
    start = None
    end = None

    for occurrence in event.occurrence_event.all():
        if occurrence.start and not start:
            start = occurrence.start
        elif occurrence.start and occurrence.start < start:
            start = occurrence.start
        if occurrence.end and not end:
            end = occurrence.end
        elif occurrence.end and occurrence.end > end:
            end = occurrence.end
    if start != event.cached_min_start:
        event.cached_min_start = start
        need_to_save=True
    if end != event.cached_max_end:
        event.cached_max_end = end
        need_to_save=True

    if need_to_save:
        event.save()


post_save.connect(update_event_cached_values, sender=Occurrence)
post_delete.connect(update_event_cached_values, sender=Occurrence)
