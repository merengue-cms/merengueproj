from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from merengue.base.admin import BaseContentAdminExtra
from merengue.base.models import BaseContent
from merengue.multimedia.admin import PendingBaseMultimediaAdmin
from merengue.multimedia.models import BaseMultimedia, Photo
from merengue.section.models import (Carousel, Section, Document,
                            AppSection, Menu, CustomStyle)
from merengue.event.models import Event

from merengue.base.admin import LogEntryRelatedContentModelAdmin

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
