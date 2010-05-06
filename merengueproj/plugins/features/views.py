from django.shortcuts import get_object_or_404

from merengue.base.views import content_view, content_list
from plugins.features.models import Feature


def features_index(request):
    feature_list = Feature.objects.published()
    return content_list(request, feature_list,
                        template_name='features/features_index.html')


def features_view(request, features_slug):
    feature_view = get_object_or_404(Feature, slug=features_slug)
    return content_view(request, feature_view,
                        template_name='features/features_view.html')
