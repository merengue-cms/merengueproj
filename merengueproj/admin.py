from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from merengue.base.admin import BaseContentAdminExtra
from merengue.base.models import BaseContent, ContactInfo
from merengue.multimedia.admin import BaseMultimediaRelatedAddContentModelAdmin, \
                             BaseMultimediaRelatedRemoveContentModelAdmin, \
                             PendingBaseMultimediaAdmin
from merengue.multimedia.models import BaseMultimedia, Photo, Video, PanoramicView, Image3D
from merengue.places.models import Location
from merengue.section.models import (Carousel, Section, Document,
                            AppSection, Menu, CustomStyle)
from merengue.event.models import Event
from merengue.event.admin import setup_event_admin

from merengue.base.admin import (BaseContentRelatedLocationModelAdmin,
                        BaseContentRelatedContactInfoAdmin,
                        BaseContentRelatedItemsRelatedModelAdmin,
                        BaseContentRelatedPhotoModelAdmin,
                        BaseContentRelatedVideoModelAdmin,
                        BaseContentRelatedPanoramicViewModelAdmin,
                        BaseContentRelatedImage3DModelAdmin,
                        LogEntryRelatedContentModelAdmin)

from merengue.base.admin import site, get_subclasses_registry_in_admin

from merengue.section.admin import (CarouselRelatedAddPhotoModelAdmin,
                           CarouselRelatedRemovePhotoModelAdmin,
                           BaseSectionRelatedDocumentModelAdmin,
                           BaseSectionRelatedMenuModelAdmin,
                           BaseSectionRelatedCustomStyleModelAdmin)

IGNORE_CONTACT_ADMIN_MODEL = (Event, )
IGNORE_LOCATION_ADMIN_MODEL = (Event, )


class AppAdminSite(admin.AdminSite):
    """ Configuracion de las interfaces de administracion para subclases de BaseContent """

    def __init__(self, model, model_admin=None):
        self.model = model
        self.model_admin = model_admin
        super(AppAdminSite, self).__init__()

    def root(self, request, url, basecontent_id=None):
        app_label = self.model._meta.app_label
        module_name = self.model._meta.module_name
        self.basecontent = get_object_or_404(self.model, id=basecontent_id)
        if url in ('', '%s/' % app_label):
            return HttpResponseRedirect("/admin/%s/%s/" % (app_label, module_name))
        return super(AppAdminSite, self).root(request, url)


def setup_basecontents_admin():
    app_admin_sites = []
    for model, model_admin in get_subclasses_registry_in_admin(BaseContent, admin_site=site):
        app_admin_site = AppAdminSite(model, model_admin)
        if model in IGNORE_CONTACT_ADMIN_MODEL:
            app_admin_site.no_contact = True
        else:
            app_admin_site.register(ContactInfo, BaseContentRelatedContactInfoAdmin)
        if model in IGNORE_LOCATION_ADMIN_MODEL:
            app_admin_site.no_location = True
        else:
            app_admin_site.register(Location, BaseContentRelatedLocationModelAdmin)
        app_admin_site.register(Photo, BaseContentRelatedPhotoModelAdmin)
        app_admin_site.register(Video, BaseContentRelatedVideoModelAdmin)
        app_admin_site.register(PanoramicView, BaseContentRelatedPanoramicViewModelAdmin)
        app_admin_site.register(Image3D, BaseContentRelatedImage3DModelAdmin)
        app_admin_site.register(BaseContent, BaseContentRelatedItemsRelatedModelAdmin)
        if model == Event:
            setup_event_admin(app_admin_site)
        app_admin_sites.append((model, app_admin_site, 'admin'))
    return app_admin_sites


def setup_sections_admin():
    carousel_admin_site_add = AppAdminSite(Carousel)
    carousel_admin_site_add.register(Photo, CarouselRelatedAddPhotoModelAdmin)
    carousel_admin_site_remove = AppAdminSite(Carousel)
    carousel_admin_site_remove.register(Photo, CarouselRelatedRemovePhotoModelAdmin)

    section_admin_site = AppAdminSite(Section)
    section_admin_site.register(Document, BaseSectionRelatedDocumentModelAdmin)
    section_admin_site.register(Menu, BaseSectionRelatedMenuModelAdmin)
    section_admin_site.register(CustomStyle, BaseSectionRelatedCustomStyleModelAdmin)
    appsection_admin_site = AppAdminSite(AppSection)
    appsection_admin_site.register(Document, BaseSectionRelatedDocumentModelAdmin)
    appsection_admin_site.register(Menu, BaseSectionRelatedMenuModelAdmin)
    #appsection_admin_site.register(CustomStyle, BaseSectionRelatedCustomStyleModelAdmin)
    return [(Carousel, carousel_admin_site_add, 'admin_add'),
            (Carousel, carousel_admin_site_remove, 'admin_remove'),
            (Section, section_admin_site, 'admin'),
            (AppSection, appsection_admin_site, 'admin'),
           ]


def setup_multimedia_admin():
    multimedia_admin_sites = []
    for model, model_admin in get_subclasses_registry_in_admin(BaseMultimedia, admin_site=site):
        multimedia_admin_site_add = AppAdminSite(model, model_admin)
        multimedia_admin_site_add.register(BaseContent, BaseMultimediaRelatedAddContentModelAdmin)
        multimedia_admin_sites.append((model, multimedia_admin_site_add, 'admin_add'))
        multimedia_admin_site_remove = AppAdminSite(model)
        multimedia_admin_site_remove.register(BaseContent, BaseMultimediaRelatedRemoveContentModelAdmin)
        multimedia_admin_sites.append((model, multimedia_admin_site_remove, 'admin_remove'))
    return multimedia_admin_sites


def setup_user_admin():
    user_admin_site = AppAdminSite(User)
    user_admin_site.register(LogEntry, LogEntryRelatedContentModelAdmin)
    return [(User, user_admin_site, 'admin')]


class AdminSiteExtra(admin.AdminSite):

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(AdminSiteExtra, self).__init__(*args, **kwargs)


def setup_extra_admin():
    admin_site_extra_basecontent = AdminSiteExtra(BaseContent)
    admin_site_extra_basecontent.register(BaseContent, BaseContentAdminExtra)
    admin_site_extra_basemultimedia = AdminSiteExtra(BaseMultimedia)
    admin_site_extra_basemultimedia.register(BaseMultimedia, PendingBaseMultimediaAdmin)
    admin_extras = [
        (BaseContent, admin_site_extra_basecontent, 'admin/pending_contents'),
        (BaseMultimedia, admin_site_extra_basemultimedia, 'admin/pending_multimedia'),
    ]
    return admin_extras
