# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model
from django.http import (HttpResponseRedirect, HttpResponsePermanentRedirect,
                         Http404, HttpResponse)
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.importlib import import_module
from django.utils.translation import ugettext
from django.views.generic import list_detail
from django.views.decorators.cache import never_cache

from merengue.base.models import BaseContent
from merengue.perms import utils as perms_api
from tagging.models import TaggedItem, Tag


def _get_results_msg(count):
    result = ugettext('%(result_count)d %(msg_results)s found')
    return result % {'result_count': count, 'msg_results': ugettext('results')}


def public_link(request, app_label, model_name, content_id):
    """ Redirect to public page for an object """
    model = get_model(app_label, model_name)

    try:
        content = model.objects.get(pk=content_id)
    except model.DoesNotExist:
        raise Http404

    if isinstance(content, BaseContent):
        real_content = content.get_real_instance()
        if real_content is not None:
            content = real_content

    if not hasattr(content, 'get_absolute_url'):
        raise Http404

    if isinstance(content, BaseContent):
        try:
            # first we try find out if content has an user dependant URL
            response = HttpResponsePermanentRedirect(content.link_by_user(request.user))
        except NotImplementedError:
            # we use public link
            response = HttpResponsePermanentRedirect(content.public_link())
    else:
        response = HttpResponsePermanentRedirect(content.get_absolute_url())
    response['Cache-Control'] = 'no-cache'  # avoid 301 caching in some browsers like Firefox 3.5+ or Chrome
    return response


def admin_link(request, content_type, content_id, url=''):
    """ Redirect to admin change page for an object """
    try:
        ContentType.objects.get_for_id(content_type).get_object_for_this_type(id=content_id)
    except ObjectDoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('admin:admin_redirect', args=(content_type, content_id, url)))


def public_view(request, app_label, model_name, content_id, content_slug):
    """ Default public view for any content """
    model = get_model(app_label, model_name)
    content = model.objects.get(pk=content_id)
    return content_view(request, content)


def render_content(request, content, template_name=None, extra_context=None):
    """ Overridable view for a content detail page """
    if extra_context is None:
        extra_context = {}
    ctype = ContentType.objects.get_for_model(content)
    meta_tags = TaggedItem.objects.filter(content_type=ctype, object_id=content.id)
    context = {'content': content,
               'meta_tags': meta_tags,
               'base_template': 'content_view.html'}
    context.update(extra_context)
    if template_name is None:
        template_name = content._meta.content_view_template
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request))


def content_view(request, content, template_name=None, extra_context=None):
    """ Generic view for a content detail page """
    perms_api.assert_has_permission(content, request.user, 'view')
    if content._meta.content_view_function is not None:
        func_path = content._meta.content_view_function
        func_path_join = func_path.split('.')
        render_content_view = getattr(import_module('.'.join(func_path_join[:-1])), func_path_join[-1])
    else:
        render_content_view = render_content
    return render_content_view(request, content, template_name, extra_context)


def content_list(request, queryset, paginate_by=10, page=None,
                 template_name='content_list.html', extra_context=None):
    """ Generic view for a listing page """
    extra_context = extra_context or {}
    context = {'template_base': 'base.html'}
    context.update(extra_context)
    return list_detail.object_list(request, queryset,
                                   template_name=template_name,
                                   allow_empty=True,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_object_name='content',
                                   extra_context=context)


@never_cache
def ajax_autocomplete_tags(request, app_name, model):
    cls = get_model(app_name, model)
    query_string = request.GET.get("q", None)
    limit = request.GET.get("limit", None)
    tags = Tag.objects.usage_for_model(cls)

    for subclass in cls.get_subclasses():
        tags.extend(Tag.objects.usage_for_model(subclass))
    if query_string:
        tags = [t for t in tags if query_string in t.name]
    if limit:
        tags = tags[:int(limit)]
    return HttpResponse("\n".join(["%s|%d" % (t.name, t.id) for t in tags]))
