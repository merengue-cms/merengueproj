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
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import get_language_from_request

from merengue.section.models import BaseSection, Document, \
                                    DocumentSection, BaseLink
from merengue.base.decorators import login_required
from merengue.base.views import content_view
from merengue.section.models import AbsoluteLink, ContentLink, ViewletLink, Menu
from merengue.section.utils import get_section

from merengue.perms import utils as perms_api


def section_index(request):
    """ place holder to have reverse URL resolution """
    return HttpResponse('')


def section_view(request, section_slug, original_context={},
                 template='section/section_view_without_maincontent.html'):
    section_slug = section_slug.strip('/')
    section = get_object_or_404(BaseSection, slug=section_slug)

    perms_api.assert_has_permission(section, request.user, 'view')
    context = original_context or {}
    context['section'] = section.get_real_instance()
    main_content = section.main_content and section.main_content.get_real_instance() or None
    if not main_content:
        return section_view_without_maincontent(request, context, template)
    template_name = getattr(main_content._meta, 'content_view_template')
    return content_view(request, main_content, template_name=template_name, extra_context=context)


def content_section_view(request, section_slug, content_id, content_slug):
    section = get_object_or_404(BaseSection, slug=section_slug)
    content = section.related_content.get(pk=content_id).get_real_instance()
    template_name = getattr(content._meta, 'content_view_template')
    return content_view(request, content, template_name=template_name)


def document_section_view(request, section_slug, document_id, document_slug):
    document = get_object_or_404(Document, pk=document_id)
    template_name = getattr(document._meta, 'content_view_template')
    return content_view(request, document, template_name=template_name)


def menu_section_view(request, section_slug, menu_slug):
    menu = None
    if section_slug:
        section = get_object_or_404(BaseSection, slug=section_slug)
    else:
        section = get_section(request=request)
    if section:
        root_menu = section.main_menu
    else:
        root_menu = Menu.objects.get(slug=settings.MENU_PORTAL_SLUG)
    try:
        menu = root_menu.get_descendants_by_user(request.user).get(slug=menu_slug)
    except Menu.DoesNotExist:
        try:
            if not section_slug:
                # Other tree menu, different of menu portal slug
                menu = Menu.tree.get(slug=menu_slug)
                root_menu = menu.get_root()
            else:
                raise Http404
        except Menu.DoesNotExist:
            raise Http404

    try:
        link = menu.baselink.real_instance
    except BaseLink.DoesNotExist:
        can_edit = False
        if section:
            can_edit = section.can_edit(request.user)
        else:
            can_edit = menu.can_edit(request.user)
        return render_to_response('section/menu_link_not_exists.html',
            {'menu': menu, 'can_edit': can_edit}, context_instance=RequestContext(request))
    if isinstance(link, AbsoluteLink):
        url_redirect = link.get_absolute_url()
        if  url_redirect != request.get_full_path():
            return HttpResponseRedirect(url_redirect)
        raise Http404
    else:
        context = {}
        if section_slug:
            context['section'] = section.get_real_instance()
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


def section_view_without_maincontent(request, context,
                                     template='section/section_view_without_maincontent.html'):
    user = request.user
    section = context['section']
    admin_absolute_url = False
    if section.can_edit(user):
        admin_absolute_url = True
    context['admin_absolute_url'] = admin_absolute_url
    return render_to_response(template, context,
                              context_instance=RequestContext(request))


def section_custom_style(request, section_slug):
    section = get_object_or_404(BaseSection, slug=section_slug)
    return render_to_response('section/section_colors.css',
                              {'customstyle': section.customstyle},
                              context_instance=RequestContext(request),
                              mimetype='text/css')


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
    kwargs = dict(section_slug=parts[0])
    func = None

    if url.startswith(settings.MEDIA_URL):
        raise Http404  # shortcut to avoid uneeded cpu cycles
    if len(parts) == 1:
        func = section_view
    elif len(parts) == 4 and parts[1] == 'contents':
        func = content_section_view
        kwargs.update({'content_id': parts[2], 'content_slug': parts[3]})
    elif len(parts) == 4 and parts[1] == 'doc':
        func = document_section_view
        kwargs.update({'document_id': parts[2], 'document_slug': parts[3]})
    elif len(parts) >= 2:
        func = menu_section_view
        kwargs.update({'menu_slug': parts[-1]})
    elif not url.startswith('/sections'):
        return HttpResponseRedirect('/sections%s' % url)
    else:
        raise Http404
    return func(request, **kwargs)


@login_required
def insert_document_section_after(request):
    document_id = request.GET.get('document_id', None)
    document_section_id = request.GET.get('document_section_id', None)
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
def document_section_delete(request):
    document_section_id = request.GET.get('document_section_id', None)
    section = get_object_or_404(DocumentSection, id=document_section_id)
    section.delete()
    json_dict = simplejson.dumps({'errors': 0})
    return HttpResponse(json_dict, mimetype='text/plain')


@login_required
def document_section_edit(request):
    document_section_id = request.POST.get('document_section_id', None)
    document_section_body = request.POST.get('document_section_body', None)
    section = get_object_or_404(DocumentSection, id=document_section_id)
    lang = get_language_from_request(request)
    setattr(section, 'body_' + lang, document_section_body)
    section.save()
    json_dict = simplejson.dumps({'errors': 0, 'body': section.body})
    return HttpResponse(json_dict, mimetype='text/plain')


@login_required
def document_section_move(request):
    document_section_id = request.GET.get('document_section_id', None)
    prevsection = request.GET.get('document_section_prev', None)
    nextsection = request.GET.get('document_section_next', None)
    section = get_object_or_404(DocumentSection, id=document_section_id)
    if nextsection:
        next_section = get_object_or_404(DocumentSection, id=nextsection)
        if next_section.position > section.position:
            position = next_section.position - 1
            if position < 0:
                position = 0
        else:
            position = next_section.position
        section.move_to(position)
    elif prevsection:
        prev_section = get_object_or_404(DocumentSection, id=prevsection)
        if prev_section.position > section.position:
            position = prev_section.position
        else:
            position = prev_section.position + 1
        section.move_to(position)
    json_dict = simplejson.dumps({'errors': 0, 'position': section.position})
    return HttpResponse(json_dict, mimetype='text/plain')
