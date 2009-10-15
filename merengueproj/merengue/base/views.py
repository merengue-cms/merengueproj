from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
#from django.db import connection
from django.db.models import get_model
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import list_detail

from cmsutils.adminfilters import QuerySetWrapper, filter_by_query_string

from merengue.base.forms import CaptchaFreeThreadedCommentForm
from threadedcomments.models import FreeThreadedComment

from merengue.base.models import BaseContent
from captcha.decorators import add_captcha
from merengue.places.forms import SearchFilter
from rating.models import Vote


def add_related_content(filters):
    new_filters = filters
    for filter_key, filter_value in filters.items():
        if filter_key.startswith('location'):
            new_filters['related_items__%s' % filter_key] = new_filters[filter_key]
            del new_filters[filter_key]
    return new_filters


def make_hidden_split(list_fields):

    def filter_processor(filters):
        for field in list_fields:
            values = filters.get(field, None)
            if values and len(values) > 1 and isinstance(values, list):
                del values[len(values)-1]
        return filters
    return filter_processor


def is_null_processor(filters):
    for key, value in filters.items():
        if key.endswith('__isnull'):
            if value.isdigit():
                filters.update({key: bool(int(value))})
            else:
                filters.update({key: value == 'True'})
    return filters


def get_results_msg(count):
    result = ugettext('%(result_count)d %(msg_results)s found')
    return result % {'result_count': count, 'msg_results': ugettext('results')}


def search_results(request, search_form, original_context={}):
#    params_form = params_form or {}
#    search_form_class = get_search_form_class(request)
#    search_form = search_form_class(**params_form)

    if request.is_ajax():
        return search_form.render_search_results_map(request)

    results = search_form.search_results(request)

    result_msg = get_results_msg(results.count())

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
        if hasattr(content, 'public_link'):
            return HttpResponseRedirect(content.public_link())
        else:
            return HttpResponseRedirect(content.link_by_user(request.user))

    return HttpResponseRedirect(content.get_absolute_url())


def admin_link(request, content_type, content_id, url=''):
    """ Redirect to admin change page for an object """
    try:
        content = ContentType.objects.get_for_id(content_type).get_object_for_this_type(id=content_id)
    except ObjectDoesNotExist:
        raise Http404

    admin_prefix = '/admin/'
    return HttpResponseRedirect(reverse('admin:admin_redirect', args=(content_type, content_id, )))


@add_captcha(CaptchaFreeThreadedCommentForm)
def content_comment_form(request, content, parent_id, form=None, template='base/content_comment_add.html'):
    if not form or form.content.get_real_instance() != content:
        form = CaptchaFreeThreadedCommentForm(user=request.user)
        form.content = content

    if request.user:
        form.initial = {'name': request.user.username}
    content_type = ContentType.objects.get_for_model(content)

    return render_to_response(template,
                              {'content_id': content.id,
                               'content_type_id': content_type.id,
                               'content': content,
                               'comment': form.instance,
                               'parent_id': parent_id,
                               'form': form,
                              },
                              context_instance=RequestContext(request))


def content_view(request, content, template_name=None, extra_context=None):
    """ Generic view for a content detail page """
    if extra_context is None:
        extra_context = {}
    context = {'content': content}
    context.update(extra_context)
    if template_name is None:
        template_name = content._meta.content_view_template
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request))


def generic_object_list(request, queryset, title, menu_selected,
                        base_template, child_template_name,
                        original_context={},
                        template_name='base/generic_object_list.html',
                        filter_func=None):

    extra_context = dict(
        title=title,
        base_template=base_template,
        child_template=child_template_name,
        menuselected=menu_selected,
        )

    if filter_func:
        form = SearchFilter(data=request.GET, show_city_field=False, filters={})
        if form.is_valid():
            form.filters['id__in'] = [x.id for x in queryset]
            queryset = filter_func(queryset, request)
            form.recommended_other_words(queryset)
        extra_context['form'] = form
    extra_context.update(original_context)

    return list_detail.object_list(request, queryset,
                                   template_name=template_name,
                                   allow_empty=True,
                                   extra_context=extra_context,
                                   template_object_name='object')


def top_rated_filter(queryset, request):
    name_value = request.GET.get('name__icontains', None)
    if name_value is None:
        return queryset
    data = [obj for obj in queryset.data if name_value.lower() in obj.name.lower()]
    queryset.data = data
    return queryset


def most_commented_filter(queryset, request):
    queryset, qsm = filter_by_query_string(request, queryset,
                                           page_var=settings.PAGE_VARIABLE)
    obj_ids = []
    for obj in queryset:
        if obj.comment_number > 0:
            obj_ids.append(obj.id)
    return queryset.filter(pk__in=obj_ids)


def top_rated_list(request, model, base_template,
                   title=_('The most rated ones'),
                   template_name='base/generic_object_list.html',
                   child_template_name='base/top_rated_item.html',
                   original_context={}):
    top_rated = Vote.objects.get_top(model, limit=None)
    top_rated_objects = []
    for rated in top_rated:
        obj = rated[0]
        obj.comment_number = FreeThreadedComment.objects.all_for_object(obj).count()
        top_rated_objects.append(obj)
    top_rated_objects = QuerySetWrapper(top_rated_objects)

    return generic_object_list(request, top_rated_objects, title,
                               'top-rated', base_template, child_template_name,
                               original_context, filter_func=top_rated_filter)


def most_commented_list(request, model, base_template,
                        title=_('The most commented ones'),
                        child_template_name='base/most_commented_item.html',
                        original_context={}):
    most_commented_objects = model.objects.published().with_comment_number(True)
    return generic_object_list(request, most_commented_objects, title,
                               'most-commented', base_template, child_template_name,
                               original_context, filter_func=most_commented_filter)
