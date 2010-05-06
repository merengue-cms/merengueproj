from merengue.base.admin import BaseContentAdmin, BaseCategoryAdmin
from plugins.features.models import Feature, FeatureCategory


class FeatureCategoryAdmin(BaseCategoryAdmin):
    pass


class FeatureAdmin(BaseContentAdmin):
    ordering = ('name_es', )
    search_fields = ('name', )
    list_display = ('name', )


def register(site):
    site.register(FeatureCategory, FeatureCategoryAdmin)
    site.register(Feature, FeatureAdmin)


def unregister(site):
    site.unregister(FeatureCategory)
    site.unregister(Feature)
