from django.conf import settings
from django.contrib.contenttypes.models import ContentType
#from django.db import connection
from django.db.models import get_model
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import list_detail

from cmsutils.adminfilters import QuerySetWrapper, filter_by_query_string

from base.forms import CaptchaFreeThreadedCommentForm
from threadedcomments.models import FreeThreadedComment

from base.models import BaseContent
from base.utils import invalidate_cache_for_path
from captcha.decorators import add_captcha
from places.forms import SearchFilter
from rating.models import Vote


CONVERT_PRICE = SortedDict((
                    ('0',
                        {'operator': 'lte', 'value': 50, 'label': _('less than 50')}),
                    ('50',
                        {'operator': 'lte', 'value': 100, 'label': _('from 50 to 100')}),
                    ('100',
                        {'operator': 'lte', 'value': 300, 'label': _('from 100 to 300')}),
                    ('300',
                        {'label': _('greater than 300')}),
                ))


def add_price_lte(filters):

    new_filters = filters
    if 'price__gte' in new_filters:
        price__gte = filters['price__gte']
        converter = CONVERT_PRICE.get(price__gte, None)
        operator = converter.get('operator', None)
        value = converter.get('value', None)
        if converter and operator and value:
            new_filters['price__%s' % operator] = value
    elif 'price__in' in new_filters:
        values = [int(val) for val in new_filters['price__in']]
        max_value = max(values)
        min_value = min(values)
        new_filters['price__gte'] = min_value
        converter = CONVERT_PRICE.get(unicode(max_value), None)
        converter_value = converter and converter.get('value', None)
        if converter and converter_value:
            new_filters['price__lte'] = converter_value
        del new_filters['price__in']
    return new_filters


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
        real_content = content._get_real_instance()
        if real_content is not None:
            content = real_content

    if not hasattr(content, 'get_absolute_url'):
        raise Http404

    if isinstance(content, BaseContent):
        app_section_name = settings.APP_SECTION_MAP[content.get_class_name()]
        if (settings.SECTION_MAP[app_section_name]['published'] or request.user.is_staff) \
            and hasattr(content, 'public_link'):
            # content will go to new django system if:
            #  a) section is published
            #  b) even if section was not published, I'm staff people
            #     because I have to access to new URL for reviewing tasks
            return HttpResponseRedirect(content.public_link())
        else:
            return HttpResponseRedirect(content.link_by_user(request.user))

    if hasattr(content, 'get_plone_link'):
        return HttpResponseRedirect(content.get_plone_link())

    return HttpResponseRedirect(content.get_absolute_url())


def admin_link(request, content_type, content_id, url=''):
    """ Redirect to admin change page for an object """
    try:
        content = ContentType.objects.get_for_id(content_type).get_object_for_this_type(id=content_id)
    except:
        return HttpResponseRedirect('#')

    if isinstance(content, BaseContent):
        real_content = content._get_real_instance()
        if real_content is not None:
            content = real_content

    return HttpResponseRedirect('/admin/%s/%s/%d/%s' % (content._meta.app_label,
                                    content._meta.module_name, content.id, url))


@add_captcha(CaptchaFreeThreadedCommentForm)
def content_comment_form(request, content, parent_id, form=None, template='base/content_comment_add.html'):
    if not form or form.content._get_real_instance() != content:
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


@never_cache
@add_captcha(CaptchaFreeThreadedCommentForm)
def content_comment_add(request, content_type, content_id, parent_id=None):
    """ Create or save a freecomment form """
    content = BaseContent.objects.get(id=content_id)
    content = content._get_real_instance()
    if request.POST:

        form = CaptchaFreeThreadedCommentForm(user=request.user, data=request.POST)
    else:
        if request.is_ajax():
            return content_comment_form(request, content, parent_id)
        else:
            return content_comment_form(request, content, parent_id,
                              template='base/content_comment_preview.html')

    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.ip_address = request.META.get('REMOTE_ADDR', None)
        new_comment.content_type = get_object_or_404(ContentType, id=int(content_type))
        new_comment.object_id = int(content_id)
        if parent_id:
            new_comment.parent = get_object_or_404(FreeThreadedComment, id=int(parent_id))
        new_comment.save()

        # invalidate content view for avoid anonymous cache issues (see ticket #2459)
        invalidate_cache_for_path(content.public_link())

        if request.user and not request.user.is_anonymous():
            request.user.message_set.create(message="Your message has been posted successfully.")
        else:
            request.session['successful_data'] = {
                'name': form.cleaned_data['name'],
                'website': form.cleaned_data['website'],
                'email': form.cleaned_data['email'],
            }
        if request.is_ajax():
            moderation = request.user and request.user.is_staff
            return render_to_response('base/content_comment.html',
                                      {'content': content,
                                       'content_id': content_id,
                                       'content_type_id': content_type,
                                       'parent_id': parent_id,
                                       'show_links': True,
                                       'moderation': moderation,
                                       'show_children': False,
                                       'comment': new_comment},
                                       context_instance=RequestContext(request))

        else:
            return HttpResponseRedirect(content.get_absolute_url())
    else:
        if request.is_ajax():
            return render_to_response('base/content_comment_add.html',
                                  {'form': form,
                                   'content': content,
                                   'content_id': content_id,
                                   'content_type_id': content_type,
                                   'parent_id': parent_id,
                                   'comment': form.instance,
                                   'errors': form.errors},
                                  context_instance=RequestContext(request))
        return render_to_response('base/content_comment_preview.html',
                                  {'form': form,
                                   'content': content,
                                   'content_id': content_id,
                                   'content_type_id': content_type,
                                   'parent_id': parent_id,
                                   'comment': form.instance,
                                   'errors': form.errors},
                                  context_instance=RequestContext(request))


def content_comment_change_visibity(request, comment_id, publish=True):
    """ Change visibility status for a commnet """
    comment = get_object_or_404(FreeThreadedComment, id=comment_id)
    content = comment.content_object
    if request.user and not request.user.is_staff:
        return HttpResponseRedirect(content.get_absolute_url())

    comment.is_public = not comment.is_public
    comment.save()
    if request.is_ajax():
        json = simplejson.dumps({'is_public': comment.is_public}, ensure_ascii=False)
        return HttpResponse(json, 'text/javascript')
    else:
        return HttpResponseRedirect(content.get_absolute_url())


def content_comment_delete(request, comment_id):
    """ Delete comment from database """
    comment = get_object_or_404(FreeThreadedComment, id=comment_id)
    content = comment.content_object

    if request.user and not request.user.is_staff:
        return HttpResponseRedirect(content.get_absolute_url())

    comment.delete()
    if request.is_ajax():
        json = simplejson.dumps({'is_deleted': True}, ensure_ascii=False)
        return HttpResponse(json, 'text/javascript')
    else:
        return HttpResponseRedirect(content.get_absolute_url())


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
