import operator
import re

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis import admin as geoadmin
from django.contrib.gis.maps.google import GoogleMap
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from base.admin import BaseAdmin, transmeta_aware_fieldname,\
                       BaseContentRelatedMultimediaModelAdmin, VideoChecker,\
                       WorkflowBatchActionProvider
from multimedia.models import Photo, Video, PanoramicView, Image3D
from places.models import (BaseDestination, Province, BaseCity, Village, City,
                           TouristZone, Location, AddressType,
                           MultimediaProvinceRel, MultimediaTouristZoneRel,
                           MultimediaBaseCityRel)
from transmeta import get_real_fieldname_in_each_language


GMAP = GoogleMap(key=settings.GOOGLE_MAPS_API_KEY)


class GoogleAdmin(geoadmin.OSMGeoAdmin, BaseAdmin):
    extra_js = [GMAP.api_url + GMAP.key]
    map_width = 500
    map_height = 300
    default_zoom = 10
    default_lat = 4500612.0
    default_lon = -655523.0
    map_template = 'gis/admin/google.html'


def comes_from_buildbot(request):
    if hasattr(settings, 'BUILDBOT_IP'):
        if request.META.get('REMOTE_ADDR') == settings.BUILDBOT_IP:
            return True
    return False


def is_body_field(field):
    return field.startswith('body_') and len(field) != 7


class BaseDestinationAdmin(GoogleAdmin, WorkflowBatchActionProvider):
    batch_actions = BaseAdmin.batch_actions + ['set_as_draft', 'set_as_pending',
                                               'set_as_published', 'set_as_pasive']
    batch_actions_perms = {'set_as_draft': 'base.can_draft',
                           'set_as_pending': 'base.can_pending',
                           'set_as_pasive': 'base.can_pasive',
                           'set_as_published': 'base.can_published',
    }

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
        super(BaseDestinationAdmin, self).save_model(request, obj, form, change)

    def _main_fields(self):
        all_fields = self.model._meta.get_all_field_names()
        fields = [f for f in all_fields if not is_body_field(f)]
        return fields

    main_fields = property(_main_fields)

    def _body_fields(self):
        all_fields = self.model._meta.get_all_field_names()
        fields = [f[:-3] for f in all_fields if is_body_field(f)]
        return list(set(fields)) # remove duplicates

    body_fields = property(_body_fields)

    def __call__(self, request, url):
        self.comes_from_buildbot = comes_from_buildbot(request)
        self.in_body_view = False

        if url is not None:
            match = re.match(r'(\d+)/bodies$', url)
            if match is not None:
                return HttpResponseRedirect('accommodation/') # first body

            body_fields = '|'.join(self._body_fields_without_prefix())
            match = re.match(r'(\d+)/bodies/(%s)$' % body_fields, url)
            if match is not None:
                self.in_body_view = True
                object_id, body_field = match.groups()
                body_field = "body_" + body_field
                self.current_body_field = body_field
                return self.body_view(request, object_id)

        return super(BaseDestinationAdmin, self).__call__(request, url)

    def change_view(self, request, object_id, extra_context=None):
        context = extra_context or {}
        if 'selected' not in context:
            context['selected'] = 'view'
        context.update({'has_bodies': True,
                        'has_media': hasattr(self.model, 'multimedia'),
                       })
        return super(BaseDestinationAdmin, self).change_view(request,
                                                            object_id,
                                                            context)

    def body_view(self, request, object_id, extra_context=None):
        context = extra_context or {}
        context['selected'] = 'bodies'
        context['body_fields'] = [{'title': ugettext("%s_menu" % f), 'name': f}
                                  for f in self._body_fields_without_prefix()]
        context['current_body_field'] = self.current_body_field.replace("body_", "")
        return self.change_view(request, object_id, context)

    def _body_fields_without_prefix(self):
        return [f.replace("body_", "") for f in self.body_fields]

    def _real_body_fields(self, exception=None):
        field_list = [get_real_fieldname_in_each_language(f)
                      for f in self.body_fields if f != exception]
        return reduce(operator.add, field_list)

    def get_form(self, request, obj=None, **kwargs):
        if self.in_body_view:
            kwargs['exclude'] = (self.main_fields
                                 + self._real_body_fields(self.current_body_field))
        else:
            kwargs['exclude'] = self._real_body_fields()

        if self.comes_from_buildbot:
            kwargs['exclude'].extend(['main_location', 'gps_location', 'borders'])
        return super(BaseDestinationAdmin, self).get_form(request, obj, **kwargs)

    def _media(self):
        if not self.comes_from_buildbot:
            media = geoadmin.OSMGeoAdmin._media(self)
        else:
            media = BaseAdmin._media(self)
        return media

    media = property(_media)


class BaseDestinationRelatedMultimediaModelAdmin(BaseContentRelatedMultimediaModelAdmin, WorkflowBatchActionProvider):
    batch_actions = BaseAdmin.batch_actions + ['set_as_draft', 'set_as_pending',
                                               'set_as_published', 'set_as_pasive']
    batch_actions_perms = {'set_as_draft': 'base.can_draft',
                           'set_as_pending': 'base.can_pending',
                           'set_as_pasive': 'base.can_pasive',
                           'set_as_published': 'base.can_published',
    }

    def _update_extra_context(self, extra_context=None):
        extra_context = super(BaseDestinationRelatedMultimediaModelAdmin, self)._update_extra_context(extra_context)
        model = self.admin_site.basecontent.__class__
        basedestination_type_id = ContentType.objects.get_for_model(model).id
        extra_context.update({'basedestination': self.admin_site.basecontent,
                              'basedestination_type_id': basedestination_type_id,
                              'is_destination': True})
        return extra_context

    def _get_human_order(self, obj):
        multimedia_rel = self._get_multimedia_rel(obj)
        return multimedia_rel._get_human_order()
    _get_human_order.short_description = _('Human Order')

    def save_model(self, request, obj, form, change):
        destination = self.admin_site.basecontent
        super(BaseContentRelatedMultimediaModelAdmin, self).save_model(request, obj, form, change)
        multimedia_rel = self._get_multimedia_rel(obj)

        if multimedia_rel:
            multimedia_rel.save()

    def reorder_view(self, request):
        destination = self.admin_site.basecontent
        if isinstance(destination, Province):
            model = MultimediaProvinceRel
            filter = {'province': destination,
                       'basemultimedia__class_name': self.model._meta.module_name}
        if isinstance(destination, TouristZone):
            model = MultimediaTouristZoneRel
            filter = {'touristzone': destination,
                       'basemultimedia__class_name': self.model._meta.module_name}
        if isinstance(destination, BaseCity):
            model = MultimediaBaseCityRel
            filter = {'basecity': destination,
                       'basemultimedia__class_name': self.model._meta.module_name}

        if request.method == 'POST':
            order = 0
            for multimediarel_id in request.POST['multimedias'].split(u','):
                if multimediarel_id:
                    multimediarel = model.objects.get(id=int(multimediarel_id))
                    multimediarel.order = order
                    order += 1
                    multimediarel.save()

            if u'_continue' in request.POST:
                next = '.'
            else:
                next = '../'

            return HttpResponseRedirect(next)

        multimediarelations = model.objects.filter(**filter).order_by('order')
        context = {'title': _(u'Reorder view'),
                   'change': True,
                   'reorder': True,
                   'app_label': destination._meta.app_label,
                   'opts': self.opts,
                   'multimediarelations': multimediarelations,
                  }

        context.update(self._update_extra_context())
        return render_to_response('admin/reorder.html', context,
                                 context_instance=RequestContext(request))

    def _get_multimedia_rel(self, multimedia):
        destination = self.admin_site.basecontent
        basemultimedia = multimedia.basemultimedia_ptr

        if isinstance(destination, Province):
            obj, created = MultimediaProvinceRel.objects.get_or_create(province=destination,
                            basemultimedia=basemultimedia)
        if isinstance(destination, TouristZone):
            obj, created = MultimediaTouristZoneRel.objects.get_or_create(touristzone=destination,
                            basemultimedia=basemultimedia)
        if isinstance(destination, BaseCity):
            obj, created = MultimediaBaseCityRel.objects.get_or_create(basecity=destination,
                                                  basemultimedia=basemultimedia)

        return obj


class BaseDestinationRelatedPhotoModelAdmin(BaseDestinationRelatedMultimediaModelAdmin):
    list_display = ('__str__', 'admin_thumbnail', 'status', '_get_human_order')
    list_filter = ('status', )
    search_fields = ('name', 'original_filename')
    selected = 'photos'
    html_fields = ('caption', )

    def queryset(self, request):
        basemultimedia_ids = [bm.id for bm in self.admin_site.basecontent.multimedia.photos()]
        return Photo.objects.filter(basemultimedia_ptr__id__in=basemultimedia_ids)


class BaseDestinationRelatedVideoModelAdmin(VideoChecker, BaseDestinationRelatedMultimediaModelAdmin):
    list_display = ('__str__', 'admin_thumbnail', 'status', '_get_human_order')
    list_filter = ('status', )
    search_fields = ('name', 'original_filename')
    selected = 'videos'

    def queryset(self, request):
        basemultimedia_ids = [bm.id for bm in self.admin_site.basecontent.multimedia.videos()]
        return Video.objects.filter(basemultimedia_ptr__id__in=basemultimedia_ids)


class BaseDestinationRelatedPanoramicViewModelAdmin(BaseDestinationRelatedMultimediaModelAdmin):
    list_display = ('__str__', 'admin_thumbnail', 'status', '_get_human_order')
    list_filter = ('status', )
    search_fields = ('name', 'original_filename')
    selected = 'panoramics'

    def queryset(self, request):
        basemultimedia_ids = [bm.id for bm in self.admin_site.basecontent.multimedia.panoramic_views()]
        return PanoramicView.objects.filter(basemultimedia_ptr__id__in=basemultimedia_ids)


class BaseDestinationRelatedImage3DModelAdmin(BaseDestinationRelatedMultimediaModelAdmin):
    list_display = ('__str__', 'status', '_get_human_order')
    list_filter = ('status', )
    search_fields = ('name', 'original_filename')
    selected = '3ds'

    def queryset(self, request):
        basemultimedia_ids = [bm.id for bm in self.admin_site.basecontent.multimedia.images3d()]
        return Image3D.objects.filter(basemultimedia_ptr__id__in=basemultimedia_ids)


class ProvinceAdmin(BaseDestinationAdmin):
    list_display = ('name', 'status')
    ordering = ('name', )
    search_fields = ('name', )
    html_fields = BaseDestination._meta.translatable_fields


class CityAdmin(BaseDestinationAdmin):
    list_display = ('name', 'city_code', 'province', 'get_touristzones_text', 'status', 'last_editor')
    list_filter = ('province', 'status', 'last_editor')
    ordering = ('name', )
    search_fields = ('name', )
    html_fields = BaseDestination._meta.translatable_fields
    default_zoom = 13


class VillageAdmin(BaseDestinationAdmin):
    list_display = ('name', 'city_code', 'province', 'get_touristzones_text', 'status', 'last_editor')
    list_filter = ('province', 'status', 'last_editor')
    ordering = ('name', )
    search_fields = ('name', )
    filter_horizontal = ('cities', )
    html_fields = BaseDestination._meta.translatable_fields


class TouristZoneAdmin(BaseDestinationAdmin):
    list_display = ('name', 'province', 'status', 'last_editor')
    search_fields = ('name', )
    list_filter = ('province', 'status', 'last_editor')
    filter_horizontal = ('cities', )
    html_fields = BaseDestination._meta.translatable_fields


class AddressTypeAdmin(BaseAdmin):
    list_display = ('name', )


class LocationAdmin(GoogleAdmin):
    filter_horizontal = ('cities', )


class BasePlaceAdmin(BaseAdmin):

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(BasePlaceAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        db_fieldname = transmeta_aware_fieldname(db_field)
        if db_fieldname == 'description':
            field.widget.attrs['rows'] = 4
        return field


class PendingBaseDestinationAdmin(BaseDestinationAdmin):
    change_list_template = 'admin/extra/change_list.html'

    def changelist_view(self, request, extra_context=None):
        template_base = 'batchadmin/change_list.html'
        return super(PendingBaseDestinationAdmin, self).changelist_view(request,
                                                                         extra_context={'template_base': template_base,
                                                                         'admin_extra': True})


admin.site.register(Province, ProvinceAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Village, VillageAdmin)
admin.site.register(TouristZone, TouristZoneAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(AddressType, AddressTypeAdmin)
