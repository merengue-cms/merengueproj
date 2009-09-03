from django.shortcuts import render_to_response
from django.template import RequestContext

from plugins.feedback.models import Feedback


def feedback_index(request):
    feedback_list = Feedback.objects.all()
    return render_to_response('feedback/feedback_index.html',
                              {'feedback_list': feedback_list},
                              context_instance=RequestContext(request))
