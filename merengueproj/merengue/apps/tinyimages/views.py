from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.generic import list_detail

from tinyimages.models import TinyImage, TinyFile
from tinyimages.forms import TinyImageForm, TinyFileForm


TINYIMAGES_RESTRICT_OWNER = getattr(settings, 'TINYIMAGES_RESTRICT_OWNER', True)


def base_list(request, form_class, model_class, template_name):
    user = request.user
    message = None
    if not user.is_authenticated():
        user = None

    query = None
    query_string = ''
    query_filter = Q()
    if request.method == 'GET' and request.GET.get('searcher', False):
        query = request.GET.get('query', '')
        query_string = 'query=%s&searcher=1&' % query
        query_filter = Q(title__icontains=query)
        if model_class == TinyFile:
            query_filter = query_filter | Q(file__icontains=query)
        form = form_class()
    elif request.method == 'POST':
        form = form_class(data=request.POST.copy(), files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = user
            obj.save()
            if form_class == TinyFileForm:
                message = _(u'Your file has been uploaded. ' +\
                            u'Now you can select it below to be added into editor')
            else:
                message = _(u'Your image has been uploaded. ' +\
                            u'Now you can select it below to be added into editor')
            form = form_class()
    else:
        form = form_class()

    if TINYIMAGES_RESTRICT_OWNER:
        owner_filter = {'owner': user}
    else:
        owner_filter = {}
    object_list = model_class.objects.filter(query_filter).filter(**owner_filter).order_by('title')
    jquery_media_url = hasattr(settings, 'JQUERY_BASE_MEDIA') and \
                       '%s%s' % (settings.MEDIA_URL, settings.JQUERY_BASE_MEDIA) or \
                       '%sjs/' % settings.MEDIA_URL

    return list_detail.object_list(request, object_list,
                               allow_empty=True,
                               template_name=template_name,
                               paginate_by=16,
                               extra_context={'form': form,
                                              'message': message,
                                              'query': query,
                                              'query_string': query_string,
                                              'jquery_media_url': jquery_media_url},
                               )


def file_list(request):
    return base_list(request, form_class=TinyFileForm, model_class=TinyFile, template_name='tinyimages/file_list.html')


def image_list(request):
    return base_list(request, form_class=TinyImageForm, model_class=TinyImage, template_name='tinyimages/image_list.html')


@login_required
def base_delete(request, obj, template_name):
    user = request.user
    if TINYIMAGES_RESTRICT_OWNER and (not user.is_superuser or not user == obj.owner):
        raise Http404

    if request.method == 'POST':
        if request.POST.get('yes', None):
            obj.delete()
        return HttpResponseRedirect('../..')

    return render_to_response(template_name,
                              {'object': obj},
                              context_instance=RequestContext(request))


def image_delete(request, image_id):
    image = get_object_or_404(TinyImage, id=image_id)
    return base_delete(request, image, template_name='tinyimages/image_delete.html')


def file_delete(request, file_id):
    file = get_object_or_404(TinyFile, id=file_id)
    return base_delete(request, file, template_name='tinyimages/file_delete.html')


def file_upload_view(request):
    return render_to_response('tinyimages/file.html',
                              {'TINYMCE_MEDIA': settings.TINYMCE_MEDIA},
                              context_instance=RequestContext(request))
