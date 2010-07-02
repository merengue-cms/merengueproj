# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
#from django.db import connection
from django.db.models import get_model
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext
from django.views.generic import list_detail

from merengue.base.models import BaseContent
from merengue.perms import utils as perms_api
from tagging.models import TaggedItem


def _get_results_msg(count):
    result = ugettext('%(result_count)d %(msg_results)s found')
    return result % {'result_count': count, 'msg_results': ugettext('results')}


def search_results(request, search_form, original_context={}):
    """ Generic view for searching results """
    if request.is_ajax():
        return search_form.render_search_results_map(request)

    results = search_form.search_results(request)

    result_msg = _get_results_msg(results.count())

    extra_context = dict(
        query_string=search_form.get_qsm().get_query_string(),
        result_msg=result_msg,
        search_form=search_form,
        base_template=search_form.base_results_template,
        menuselected=search_form.get_selected_menu(),
        )

    extra_context.update(original_context)
    return list_detail.object_list(request, results,
                                   template_name=search_form.results_template,
                                   allow_empty=True,
                                   extra_context=extra_context,
                                   template_object_name='object')


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
            return HttpResponsePermanentRedirect(content.link_by_user(request.user))
        except NotImplementedError:
            # we use public link
            return HttpResponsePermanentRedirect(content.public_link())

    return HttpResponsePermanentRedirect(content.get_absolute_url())


def admin_link(request, content_type, content_id, url=''):
    """ Redirect to admin change page for an object """
    try:
        content = ContentType.objects.get_for_id(content_type).get_object_for_this_type(id=content_id)
    except ObjectDoesNotExist:
        raise Http404
    return HttpResponseRedirect(reverse('admin:admin_redirect', args=(content_type, content_id, )))


def public_view(request, app_label, model_name, content_id, content_slug):
    """ Default public view for any content """
    model = get_model(app_label, model_name)
    content = model.objects.get(pk=content_id)
    return content_view(request, content)


def content_view(request, content, template_name=None, extra_context=None):
    """ Generic view for a content detail page """
    has_view = perms_api.has_permission(content, request.user, 'view')
    if not has_view:
        raise PermissionDenied
    if extra_context is None:
        extra_context = {}
    ctype = ContentType.objects.get_for_model(content)
    meta_tags = TaggedItem.objects.filter(content_type=ctype, object_id=content.id)
    context = {'content': content, 'meta_tags': meta_tags}
    context.update(extra_context)
    if template_name is None:
        template_name = content._meta.content_view_template
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request))


def content_list(request, queryset, paginate_by=10, page=None,
                 template_name='content_list.html', extra_context=None):
    """ Generic view for a listing page """
    return list_detail.object_list(request, queryset,
                                   template_name=template_name,
                                   allow_empty=True,
                                   paginate_by=paginate_by,
                                   page=page,
                                   template_object_name='content',
                                   extra_context=extra_context)
