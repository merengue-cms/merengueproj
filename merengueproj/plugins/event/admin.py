from django.conf import settings

from merengue.base.admin import BaseContentAdmin, RelatedModelAdmin
from plugins.event.models import Event, Category


class EventCategoryAdmin(RelatedModelAdmin):
    ordering = ('name_es', )
    search_fields = ('name_es', )


class EventAdmin(BaseContentAdmin):
    ordering = ('name_es', )
    search_fields = ('name', )
    exclude = ('expire_date', )
    list_display = ('name', 'start', 'end', 'status', 'user_modification_date',
                    'last_editor')
    if settings.USE_GIS:
        list_display = list_display + ('google_minimap', )
    list_filter = ('categories', 'status', 'user_modification_date', )


def register(site):
    site.register(Category, EventCategoryAdmin)
    site.register(Event, EventAdmin)
    site.register_related(Category, EventCategoryAdmin, related_to=Event)
