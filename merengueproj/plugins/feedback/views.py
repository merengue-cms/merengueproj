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

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.utils import simplejson
from django.utils.translation import ugettext as _

from merengue.base.decorators import login_required
from threadedcomments.models import FreeThreadedComment
from captcha.decorators import add_captcha

from plugins.feedback.forms import CaptchaFreeThreadedCommentForm


@add_captcha(CaptchaFreeThreadedCommentForm)
def content_comment_form(request, content, parent_id, form=None, template='feedback/content_comment_add.html'):
    if not form:
        if request.POST:
            form = CaptchaFreeThreadedCommentForm(user=request.user, data=request.POST)
        else:
            form = CaptchaFreeThreadedCommentForm(user=request.user)

    if request.user:
        name = ''
        if hasattr(request.user, 'get_full_name'):
            name = request.user.get_full_name()
        if not name:
            name = getattr(request.user, 'username', '')
        form.initial = {'name': name,
                        'email': getattr(request.user, 'email', '')}

    content_type = ContentType.objects.get_for_model(content)

    return render_to_response(template,
                              {'content_id': content.id,
                               'content_type_id': content_type.id,
                               'content': content,
                               'comment': form.instance,
                               'parent_id': parent_id,
                               'form': form,
                               'errors': form.errors,
                              },
                              context_instance=RequestContext(request))


@never_cache
@add_captcha(CaptchaFreeThreadedCommentForm)
def content_comment_add(request, content_type, content_id, parent_id=None):
    """ Create or save a freecomment form """

    content_type = get_object_or_404(ContentType, id=int(content_type))
    content = content_type.get_object_for_this_type(id=content_id)

    if request.POST:
        form = CaptchaFreeThreadedCommentForm(user=request.user, data=request.POST)
    else:
        if request.is_ajax():
            return content_comment_form(request, content, parent_id)
        else:
            return content_comment_form(request, content, parent_id,
                              template='feedback/content_comment_preview.html')

    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.ip_address = request.META.get('REMOTE_ADDR', None)
        new_comment.content_type = content_type
        new_comment.object_id = int(content_id)
        if parent_id:
            new_comment.parent = get_object_or_404(FreeThreadedComment, id=int(parent_id))
        new_comment.save()

        if request.is_ajax():
            moderation = request.user and request.user.is_staff
            return render_to_response('feedback/content_comment.html',
                                      {'content': content,
                                       'content_id': content_id,
                                       'content_type_id': content_type.id,
                                       'parent_id': parent_id,
                                       'show_links': True,
                                       'moderation': moderation,
                                       'show_children': False,
                                       'comment': new_comment},
                                       context_instance=RequestContext(request))

        else:
            if request.user and not request.user.is_anonymous():
                request.user.message_set.create(message=_("Your message has been posted successfully."))
            else:
                request.session['successful_data'] = {
                    'name': form.cleaned_data['name'],
                    'website': form.cleaned_data['website'],
                    'email': form.cleaned_data['email'],
                }
            return HttpResponseRedirect(content.get_absolute_url())
    else:
        template = 'feedback/content_comment_preview.html'
        if request.is_ajax():
            template = 'feedback/content_comment_add.html'

        return content_comment_form(request, content, parent_id, template=template, form=form)


@login_required
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


@login_required
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
