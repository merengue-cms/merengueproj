from merengue.base.views import content_list

from plugins.fooplugin.models import FooModel


def foomodel_index(request, template_name='foomodel_index.html'):
    """ A example index views which list all the published instances """
    foo_list = FooModel.objects.published()
    return content_list(request, foo_list, template_name=template_name)
