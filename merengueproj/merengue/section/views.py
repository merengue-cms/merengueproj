from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson

from searchform.registry import search_form_registry
from merengue.section.models import BaseSection, Document, Section, \
                                    DocumentSection

from merengue.base.views import content_view
from merengue.section.models import AbsoluteLink, ContentLink, ViewletLink, Menu


def section_view(request, section_slug, original_context={}):
    section_slug = section_slug.strip('/')
    section = get_object_or_404(BaseSection, slug=section_slug)
    context = original_context or {}
    context['section'] = section.real_instance
    main_content = section.main_content and section.main_content.get_real_instance() or None
    if not main_content or not main_content.is_published():
        return section_view_whitout_maincontent(request, context)
    template_name = getattr(main_content._meta, 'content_view_template')
    return content_view(request, main_content, template_name=template_name, extra_context=context)


def content_section_view(request, section_slug, content_id, content_slug):
    section = get_object_or_404(BaseSection, slug=section_slug)
    content = section.related_content.get(pk=content_id).get_real_instance()
    template_name = getattr(content._meta, 'content_view_template')
    return content_view(request, content, template_name=template_name)


def document_section_view(request, section_slug, document_id, document_slug):
    document = get_object_or_404(Document, id=document_id)
    if not request.user.is_staff and not document.is_published():
        raise Http404
    template_name = getattr(document._meta, 'content_view_template')
    return content_view(request, document, template_name=template_name)


def menu_section_view(request, section_slug, menu_slug):
    menu = None
    if section_slug:
        section = get_object_or_404(BaseSection, slug=section_slug)
        root_menu = section.main_menu
    else:
        root_menu = Menu.objects.get(slug=settings.MENU_PORTAL_SLUG)
    try:
        menu = root_menu.get_descendants().get(slug=menu_slug)
    except Menu.DoesNotExist:
        raise Http404

    link = menu.baselink.real_instance
    if isinstance(link, AbsoluteLink):
        return HttpResponseRedirect(link.url)
    else:
        context = {}
        if section_slug:
            context['section'] = section.real_instance
        context['menu'] = menu
        if isinstance(link, ViewletLink):
            context['registered_viewlet'] = link.viewlet
            context['base_template'] = 'base.html'
            return render_to_response('section/viewlet_section_view.html', context,
                                    context_instance=RequestContext(request))
        elif isinstance(link, ContentLink):
            content = link.content.get_real_instance()
            context['base_template'] = getattr(content._meta, 'content_view_template')
            return content_view(request, content, template_name='section/menu_section_view.html', extra_context=context)


def menu_view(request, menu_slug):
    return menu_section_view(request, section_slug=None, menu_slug=menu_slug)


def section_view_whitout_maincontent(request, context):
    user = request.user
    section = context['section']
    admin_absolute_url = False
    if user.is_authenticated():
        if user.is_superuser or (user.is_staff and
                                  (user.has_perm('section.change_%s'% section._meta.module_name) or
                                  user.has_perm('section.change_basesection'))):
            admin_absolute_url = True
    context['admin_absolute_url'] = admin_absolute_url
    return render_to_response('section/section_view_whitout_maincontent.html', context,
                                  context_instance=RequestContext(request))


def section_custom_style(request, section_slug):
    section = get_object_or_404(Section, slug=section_slug)
    return render_to_response('section/section_colors.css',
                              {'customstyle': section.customstyle},
                              context_instance=RequestContext(request),
                              mimetype='text/css')


def _parse_search_form_filters(value):
    filters={}
    for filter_and_options in value.strip().split('\n'):
        if filter_and_options:
            (filter_name, options) = filter_and_options.split(':')
            filter_name = filter_name.strip()
            option_list=[]
            for option in options.strip().split(','):
                soption=option.strip()
                if soption.isdigit():
                    option_list.append(int(soption))
                else:
                    option_list.append(soption)
            filters.update({filter_name: option_list})
    return filters


@login_required
def get_search_filters_and_options(request):
    search_form = request.GET.get('search_form', None)
    widget_name = request.GET.get('widget_name', 'search_form_filters')
    value = request.GET.get('value', '')
    results = []
    actual_filters = _parse_search_form_filters(value)
    if search_form:
        search_form_class = search_form_registry.get_form_class(search_form)
        for filter in search_form_registry.get_filters(search_form):
            options=[]
            selected_options = actual_filters.get(filter, [])
            for (option_value, option_name) in search_form_registry.get_filter_options(search_form, filter):
                selected = option_value in selected_options
                options.append({'name': option_name,
                                'value': option_value,
                                'selected': selected,
                               })
            results.append({
                'label': search_form_class.fields[filter].label,
                'name': filter,
                'options': options,
            })
    return render_to_response('section/search_form_filters.html',
                              {'filters': results,
                               'widget_name': widget_name,
                               'value': value,
                              },
                              context_instance=RequestContext(request))


@login_required
def save_menu_order(request):
    for key in request.GET.keys():
        if key.startswith('menu'):
            for value in request.GET.getlist(key):
                parent_id = key[4:]
                menu_id = value
                menu = Menu.objects.get(id=menu_id)
                try:
                    parent = Menu.objects.get(id=parent_id)
                except Menu.DoesNotExist:
                    parent = menu.get_root()
                menu.move_to(parent, 'last-child')
                menu.save()
    json_dict = simplejson.dumps([])
    return HttpResponse(json_dict, mimetype='text/plain')


def section_dispatcher(request, url):
    parts = url.strip('/').split('/')
    func = None

    if len(parts) == 1:
        func = section_view
    elif len(parts) == 4 and parts[1] == 'contents':
        func = content_section_view
        del parts[1]
    elif len(parts) == 3 and parts[1] == 'doc':
        func = document_section_view
        del parts[1]
    elif len(parts) >= 2:
        func = menu_section_view
        parts = [parts[0], parts[-1]]
    elif not url.startswith('/sections'):
        return HttpResponseRedirect('/sections%s' %url)
    else:
        raise Http404
    return func(request, *parts)


@login_required
def insert_document_section_after(request, document_id, document_section_id=None):
    document = get_object_or_404(Document, id=document_id)
    if not document_section_id:
        position = 0
    else:
        section = get_object_or_404(DocumentSection, id=document_section_id)
        position = section.position + 1
    newsection = DocumentSection.objects.create(document=document)
    newsection.move_to(position)
    return render_to_response('section/document_section_view.html',
                              {'content': document,
                               'document_section': newsection,
                               'newly': True,
                              },
                              context_instance=RequestContext(request))


@login_required
def document_section_delete(request, document_id, document_section_id):
    section = get_object_or_404(DocumentSection, id=document_section_id)
    section.delete()
    json_dict = simplejson.dumps({'errors': 0})
    return HttpResponse(json_dict, mimetype='text/plain')
