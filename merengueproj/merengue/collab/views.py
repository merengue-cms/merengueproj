from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from merengue.collab.forms import CollabCommentForm, CollabCommentRevisorStatusForm
from merengue.collab.models import CollabComment
from merengue.collab.utils import get_comments_for_object


def ajax_admin_comments(request, content_type_id, content_id):
    ct = get_object_or_404(ContentType, id=content_type_id)
    try:
        content = ct.get_object_for_this_type(id=content_id)
    except models.ObjectDoesNotExist:
        raise Http404('No %s matches the given query.' % ct.model_class()._meta.object_name)

    return render_to_response('collab/collaborative_comments_view.html',
                              {'content': content,
                               'ct': ct,
                              },
                              context_instance=RequestContext(request))


def ajax_add_comment(request, content_type_id, content_id):
    ct = get_object_or_404(ContentType, id=content_type_id)
    try:
        content = ct.get_object_for_this_type(id=content_id)
    except models.ObjectDoesNotExist:
        raise Http404('No %s matches the given query.' % ct.model_class()._meta.object_name)

    message = None
    if request.method=='POST':
        form = CollabCommentForm(request.POST, content=content, request=request)
        if form.is_valid():
            message = _('Your comment has been added')
            form.save()
            form = CollabCommentForm(content=content, request=request)
    else:
        form = CollabCommentForm(content=content, request=request)
    return render_to_response('collab/collaborative_comments_add.html',
                              {'content': content,
                               'ct': ct,
                               'form': form,
                               'message': message,
                              },
                              context_instance=RequestContext(request))


def ajax_get_comment(request, comment_id):
    comment = get_object_or_404(CollabComment, id=comment_id)
    is_revisor = request.user.has_perm('can_revise')
    return render_to_response('collab/collaborative_comments_list_item.html',
                              {'comment': comment,
                               'is_revisor': is_revisor,
                              },
                              context_instance=RequestContext(request))


def ajax_revise_comment(request, comment_id):
    comment = get_object_or_404(CollabComment, id=comment_id)
    if not request.user.has_perm('can_revise'):
        raise Http404('No comment to revise.')

    message = None
    if request.method=='POST':
        form = CollabCommentRevisorStatusForm(request.POST, content=comment, request=request)
        if form.is_valid():
            message = _('Your revisor status has been added')
            form.save()
            form = CollabCommentRevisorStatusForm(content=comment, request=request)
    else:
        form = CollabCommentRevisorStatusForm(content=comment, request=request)
    return render_to_response('collab/collaborative_comments_revise.html',
                              {'comment': comment,
                               'form': form,
                               'message': message,
                              },
                              context_instance=RequestContext(request))


def ajax_list_comments(request, content_type_id, content_id):
    ct = get_object_or_404(ContentType, id=content_type_id)
    try:
        content = ct.get_object_for_this_type(id=content_id)
    except models.ObjectDoesNotExist:
        raise Http404('No %s matches the given query.' % ct.model_class()._meta.object_name)

    comments = get_comments_for_object(content)
    is_revisor = request.user.has_perm('can_revise')
    return render_to_response('collab/collaborative_comments_list.html',
                              {'content': content,
                               'comments': comments,
                               'ct': ct,
                               'is_revisor': is_revisor,
                              },
                              context_instance=RequestContext(request))


def ajax_num_comments(request, content_type_id, content_id):
    ct = get_object_or_404(ContentType, id=content_type_id)
    try:
        content = ct.get_object_for_this_type(id=content_id)
    except models.ObjectDoesNotExist:
        raise Http404('No %s matches the given query.' % ct.model_class()._meta.object_name)

    comments = get_comments_for_object(content)
    json_dict = simplejson.dumps({'num': comments.count()})
    return HttpResponse(json_dict, mimetype='application/javascript')
