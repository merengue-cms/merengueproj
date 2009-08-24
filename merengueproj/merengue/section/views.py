
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from searchform.registry import search_form_registry
from searchform.utils import search_button_submitted
from section.models import BaseSection, Document, Section

from merengue.base.views import search_results
from event.forms import EventCategoriesQuickSearchForm


def section_view(request, section_slug, original_context={}, template='section/document_view.html'):
    section_slug = section_slug.strip('/')
    section = get_object_or_404(BaseSection, slug=section_slug)
    context = {'section': section.real_instance, 'document': section.main_document}
    context.update(original_context)
    document_slug = (section.main_document and section.main_document.slug) or None
    return document_view(request, section_slug, document_slug, original_context=context, template=template)


def document_view(request, section_slug, document_slug, original_context={}, template='section/document_view.html'):
    document = document_slug and get_object_or_404(Document, slug=document_slug, related_section__slug=section_slug)
    if not document or (not document.is_published() and not request.user.is_staff):
        raise Http404
    section = (document and document.related_section) or \
               get_object_or_404(BaseSection, slug=section_slug)
    return independent_document_view(request, document, section, original_context, template)


def independent_document_view(request, document, section=None, original_context={}, template='section/document_view.html'):
    """Like document_view but with fewer restrictions"""
    search_form = document.get_search_form()
    if section is None:
        section = request.section
    context = {'document': document, 'section': section.real_instance, 'search_form': search_form}
    context.update(original_context)
    _update_context_section(context, section)

    if search_button_submitted(request):
        return search_results(request, search_form, context)
    else:
        return render_to_response(template,
                                  context,
                                  context_instance=RequestContext(request))


def section_agenda(request, section_slug, original_context={}, template='section/section_agenda.html'):
    section = get_object_or_404(BaseSection, slug=section_slug)
    search_form = EventCategoriesQuickSearchForm(section)
    context = {'section': section.real_instance, 'search_form': search_form}
    context.update(original_context)
    _update_context_section(context, section)

    if search_button_submitted(request):
        return search_results(request, search_form, context)
    else:
        return render_to_response(template,
                                  context,
                                  context_instance=RequestContext(request))


@login_required
def create_and_link_document(request, section_slug):
    if request.method == 'POST':
        s = get_object_or_404(Section, slug=section_slug)
        d = Document.objects.create(related_section=s)
        s.main_document = d
        s.save()
        return HttpResponseRedirect('/admin/section/section/%d/admin/section/document/%d/' % (s.id, d.id))
    else:
        return HttpResponseNotAllowed(['POST'])


def section_custom_style(request, section_slug):
    section = get_object_or_404(Section, slug=section_slug)
    return render_to_response('section/section_colors.css',
                              {'customstyle': section.customstyle},
                              context_instance=RequestContext(request),
                              mimetype='text/css')


def _update_context_section(context, section):
    context['event_categories'] = EventCategoriesQuickSearchForm.get_categories(section)


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


def section_dispatcher(request, url):
    parts = url.strip('/').split('/')

    if len(parts) == 2:
        return document_view(request, parts[0], parts[1])

    elif len(parts) == 1:
        return section_view(request, parts[0])

    else:
        raise Http404
