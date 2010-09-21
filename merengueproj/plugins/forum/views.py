from django.shortcuts import get_object_or_404

from merengue.base.views import content_list, content_view

from plugins.forum.models import Forum, Thread


PAGINATE_BY = 20


def forum_index(request):
    forum_list = Forum.objects.published()
    return content_list(request, forum_list, template_name='forum/forum_list.html', paginate_by=PAGINATE_BY)


def forum_view(request, forum_slug, original_context=None):
    forum = get_object_or_404(Forum, slug=forum_slug)
    context = {'thread_list': forum.thread_set.published(),
               'paginate_threads_by': PAGINATE_BY,
              }
    return content_view(request, forum, extra_context=context)


def thread_view(request, forum_slug, thread_slug, original_context=None):
    forum = get_object_or_404(Thread, slug=thread_slug)
    return content_view(request, forum)
