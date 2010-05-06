from merengue.plugin import Plugin
from plugins.features.admin import FeatureAdmin, FeatureCategoryAdmin
from plugins.features.models import Feature, FeatureCategory


class PluginConfig(Plugin):
    name = 'Features'
    description = 'Features Display Plugin'
    version = '0.0.1'
    url_prefixes = (
    ('features', 'plugins.features.urls'),
    )

    @classmethod
    def get_model_admins(cls):
        return [(Feature, FeatureAdmin),
                (FeatureCategory, FeatureCategoryAdmin)]
