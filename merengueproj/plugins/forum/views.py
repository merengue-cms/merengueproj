import transmeta

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import get_language
from django.utils.translation import ugettext as _

from captcha.decorators import add_captcha

from merengue.base.decorators import login_required
from merengue.base.utils import get_unique_slug
from merengue.base.views import content_list, content_view, render_content
from merengue.perms.utils import has_permission
from merengue.section.utils import get_section, filtering_in_section

from plugins.forum.models import Forum, Thread, ForumThreadComment
from plugins.forum.forms import CaptchaForumThreadCommentForm, CreateThreadForm
from plugins.forum.utils import can_create_new_thread


PAGINATE_BY = 20


def forum_index(request, extra_context=None):
    section = get_section(request, extra_context)
    forum_list = Forum.objects.published().order_by(transmeta.get_real_fieldname('category__name', get_language()),
                                                    transmeta.get_real_fieldname('name', get_language()))
    forum_list = filtering_in_section(forum_list, section)
    return content_list(request, forum_list, template_name='forum/forum_list.html', paginate_by=PAGINATE_BY)


def forum_view(request, forum_slug, extra_context=None):
    forum = get_object_or_404(Forum, slug=forum_slug)
    extra_context = extra_context or {}
    context = {'thread_list': forum.thread_set.published(),
               'paginate_threads_by': PAGINATE_BY,
              }
    context.update(extra_context)
    return content_view(request, forum, extra_context=context)


def content_forum_view(request, content, template_name, extra_context=None):
    extra_context = extra_context or {}
    context = {'thread_list': content.thread_set.published(),
               'paginate_threads_by': PAGINATE_BY,
              }
    context.update(extra_context)
    return render_content(request, content, template_name, context)


def thread_view(request, forum_slug, thread_slug, original_context=None):
    thread = get_object_or_404(Thread, slug=thread_slug, forum__slug=forum_slug)
    is_moderated = request.user and (request.user.is_superuser or has_permission(thread.forum, request.user, 'moderate_forum'))
    is_auth = request.user and request.user.is_authenticated()
    comments = thread.forumthreadcomment_set.filter(parent__isnull=True).order_by('date_submitted')
    if not is_moderated:
        comments = comments.filter(banned=False)
    return content_view(request, thread, extra_context={'comments': comments,
                                                        'can_comment': not thread.closed and is_auth})


def create_new_thread(request, forum_slug):
    forum = get_object_or_404(Forum, slug=forum_slug)
    http_response = can_create_new_thread(request, forum)
    if http_response:
        return http_response
    if request.POST:
        form = CreateThreadForm(forum, request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.slug = get_unique_slug(thread.name, forum.thread_set.all())
            thread.forum = forum
            thread.user = request.user
            thread.status = 'published'
            thread.save()
            workflow_status = thread.workflow_status.get_all_states().filter(slug='published')
            if workflow_status:
                thread.workflow_status = workflow_status[0]
                thread.save()
            return HttpResponseRedirect(thread.get_absolute_url())
    else:
        form = CreateThreadForm(forum)

    return render_to_response('forum/forum_create_thread.html', {
            'form': form, 'content': forum,
            }, context_instance=RequestContext(request))


@add_captcha(CaptchaForumThreadCommentForm)
def forum_comment_form(request, content, parent_id, form=None, template='forum/forum_comment_add.html'):
    if not form:
        if request.POST:
            form = CaptchaForumThreadCommentForm(user=request.user, data=request.POST)
        else:
            form = CaptchaForumThreadCommentForm(user=request.user)
    if parent_id:
        parent = get_object_or_404(ForumThreadComment, id=int(parent_id))
        form.initial = {'title': 'Re: %s' % parent.title}
    else:
        form.initial = {'title': 'Re: %s' % content.name}

    return render_to_response(template,
                              {'thread': content,
                               'comment': form.instance,
                               'parent_id': parent_id,
                               'form': form,
                               'errors': form.errors,
                              },
                              context_instance=RequestContext(request))


@login_required
def forum_comment_add(request, forum_slug, thread_slug, parent_id=None):
    thread = get_object_or_404(Thread, slug=thread_slug, forum__slug=forum_slug)
    if thread.closed:
        raise Http404

    if request.POST:
        form = CaptchaForumThreadCommentForm(user=request.user, data=request.POST)
    else:
        if request.is_ajax():
            return forum_comment_form(request, thread, parent_id)
        else:
            return forum_comment_form(request, thread, parent_id,
                              template='forum/forum_comment_preview.html')

    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.ip_address = request.META.get('REMOTE_ADDR', None)
        new_comment.user = request.user
        new_comment.thread = thread
        if parent_id:
            new_comment.parent = get_object_or_404(ForumThreadComment, id=int(parent_id))
        new_comment.save()

        if request.user and not request.user.is_anonymous():
            request.user.message_set.create(message=_("Your message has been posted successfully."))
        if request.is_ajax():
            moderation = request.user and (request.user.is_superuser or has_permission(thread.forum, request.user, 'moderate_forum'))
            is_auth = request.user and request.user.is_authenticated()
            return render_to_response('forum/thread_comment.html',
                                      {'thread': thread,
                                       'parent_id': parent_id,
                                       'is_moderated': moderation,
                                       'actions': (moderation or not thread.closed) and is_auth,
                                       'comment': new_comment},
                                       context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(thread.get_absolute_url())
    else:
        template = 'forum/forum_comment_preview.html'
        if request.is_ajax():
            template = 'forum/forum_comment_add.html'

        return forum_comment_form(request, thread, parent_id, template=template, form=form)


@login_required
def forum_comment_delete(request, comment_id):
    comment = get_object_or_404(ForumThreadComment, id=comment_id)
    content = comment.thread

    if request.user and not (request.user.is_superuser or has_permission(comment.thread.forum, request.user, 'moderate_forum')):
        return HttpResponseRedirect(content.get_absolute_url())

    comment.delete()
    if request.is_ajax():
        json = simplejson.dumps({'is_deleted': True}, ensure_ascii=False)
        return HttpResponse(json, 'text/javascript')
    else:
        return HttpResponseRedirect(content.get_absolute_url())


@login_required
def forum_comment_change_visibity(request, comment_id, publish=True):
    """ Change visibility status for a comment """
    comment = get_object_or_404(ForumThreadComment, id=comment_id)
    thread = comment.thread
    if request.user and not (request.user.is_superuser or has_permission(comment.thread.forum, request.user, 'moderate_forum')):
        return HttpResponseRedirect(thread.get_absolute_url())

    comment.banned = not comment.banned
    comment.save()
    if request.is_ajax():
        json = simplejson.dumps({'is_public': not comment.banned}, ensure_ascii=False)
        return HttpResponse(json, 'text/javascript')
    else:
        return HttpResponseRedirect(thread.get_absolute_url())
