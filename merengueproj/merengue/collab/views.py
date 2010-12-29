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

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language

from merengue.collab.forms import CollabCommentForm, CollabCommentRevisorStatusForm,\
                                  CollabTranslationForm
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
            form.save()
            message = _('Your comment has been added')
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
            form.save()
            message = _('Your revisor status has been added')
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


def ajax_admin_translation(request, content_type_id, content_id, field):
    ct = get_object_or_404(ContentType, id=content_type_id)
    try:
        content = ct.get_object_for_this_type(id=content_id)
    except models.ObjectDoesNotExist:
        raise Http404('No %s matches the given query.' % ct.model_class()._meta.object_name)

    is_html = request.GET.get('is_html', False)
    original_value = getattr(content, field, '')
    languages = settings.LANGUAGES
    current_language = get_language()
    for code, name in languages:
        if current_language == code:
            current_language = name
            break
    return render_to_response('collab/collaborative_translation_view.html',
                              {'content': content,
                               'ct': ct,
                               'field': field,
                               'original_value': original_value,
                               'current_language': current_language,
                               'is_html': is_html,
                              },
                              context_instance=RequestContext(request))


def ajax_edit_translation(request, content_type_id, content_id, field, language_id=None):
    ct = get_object_or_404(ContentType, id=content_type_id)
    try:
        content = ct.get_object_for_this_type(id=content_id)
    except models.ObjectDoesNotExist:
        raise Http404('No %s matches the given query.' % ct.model_class()._meta.object_name)

    translation_field = '%s_%s' % (field, language_id)
    translation_value = getattr(content, translation_field, '')
    current_language = get_language()
    languages = [(code, name) for code, name in settings.LANGUAGES if code!=current_language]
    language_id = language_id or languages[0][0]
    for code, name in languages:
        if language_id == code:
            translation_language = name
            translation_language_code = code
            break

    message = None
    if request.method == 'POST':
        is_html = request.POST.get('is_html', False)
        form = CollabTranslationForm(request.POST,
                                     content=content,
                                     request=request,
                                     language_code=translation_language_code,
                                     languages=languages,
                                     field=field,
                                     is_html=is_html)
        if form.is_valid():
            form.save()
            message = _('Your translation has been saved')
            form = CollabTranslationForm(content=content,
                                         request=request,
                                         language_code=translation_language_code,
                                         languages=languages,
                                         field=field,
                                         is_html=is_html)
    else:
        is_html = request.GET.get('is_html', False)
        form = CollabTranslationForm(content=content,
                                     request=request,
                                     language_code=translation_language_code,
                                     languages=languages,
                                     field=field,
                                     is_html=is_html)
    return render_to_response('collab/collaborative_translation_edit.html',
                              {'content': content,
                               'ct': ct,
                               'field': field,
                               'translation_value': translation_value,
                               'translation_language': translation_language,
                               'translation_language_code': translation_language_code,
                               'form': form,
                               'languages': languages,
                               'message': message,
                              },
                              context_instance=RequestContext(request))
