import unicodedata
import mimetypes
from os.path import join, isdir, isfile, exists
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, Http404, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.db.models import Q

from merengue.base.views import content_list
from merengue.section.utils import get_section

from plugins.filebrowser.decorators import owner_or_superuser_required, is_owner_or_superuser
from plugins.filebrowser.forms import EditDocForm, AddDocForm
from plugins.filebrowser.models import Repository, Document, FileDocument, ImageDocument
from plugins.filebrowser.templatetags.filebrowser_tags import filebrowser_reverse

from merengue.base.log import send_info, send_error


FILEBROWSER_BASE_TEMPLATE = 'base.html'


def repositories(request, extra_context=None):
    filters = {}
    section = get_section(request, extra_context)
    if section:
        filters['section'] = section
    repository_list = Repository.objects.filter(**filters)
    context = {'base_template': 'content_list.html'}
    extra_context = extra_context or {}
    context.update(extra_context)
    return content_list(request, repository_list,
                        extra_context=context,
                        template_name='filebrowser/repository_list.html')


def root(request, repository_name,
         base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    return listing(request, repository_name, path='',
                   base_template=base_template, url_prefix=url_prefix)


def listing(request, repository_name, path='',
            base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None, errornote=''):
    repository = get_object_or_404(Repository, name=repository_name)
    if path and not repository.check_dir(path):
        raise Http404

    dirs, files, parents, dirname = repository.list_directory(path)

    location = path
    if not location.endswith('/'):
        location += '/'
    documents = Document.objects.filter(repository=repository,
                                        location=location)

    edit_permission = is_owner_or_superuser(request)

    return render_to_response('filebrowser/listing.html',
                              {'repository': repository,
                               'base_template': base_template,
                               'path': path,
                               'dirs': dirs,
                               'files': files,
                               'parents': parents,
                               'dirname': dirname,
                               'errornote': errornote,
                               'documents': documents,
                               'url_prefix': url_prefix,
                               'edit_permission': edit_permission},
                              context_instance=RequestContext(request))


def search(request, base_template=FILEBROWSER_BASE_TEMPLATE):
    files, documents = (), ()
    if request.method == 'POST':
        q = request.POST.get('q').encode('utf8')
    else:
        q = ''
    repos = Repository.objects
    documents = Document.objects
    section = getattr(request, 'section', None)
    if section is not None:
        repos = repos.filter(section=section)
        documents = documents.filter(repository__in=repos)
    files = [f for repo in repos.all() for f in repo.search_files(q)]
    documents = documents.filter(Q(title__regex=q) | Q(content__regex=q))
    edit_permission = is_owner_or_superuser(request)
    return render_to_response('filebrowser/search.html',
                            {'base_template': base_template,
                            'query': q,
                            'files': files,
                            'documents': documents,
                            'edit_permission': edit_permission},
                            context_instance=RequestContext(request))


@owner_or_superuser_required
def createdir(request, repository_name, path='',
              base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    repository = get_object_or_404(Repository, name=repository_name)
    if request.POST:
        dirname = request.POST.get('dirname', None)
        dirname = dirname.strip()
        errornote = None
        if not dirname:
            errornote = _('You must introduce the name of the new folder')
        elif repository.check_dir(join(path, dirname)):
            errornote = _(u'Folder %(dirname)s already exists') % {'dirname': dirname}
        if errornote:  # si hay algun tipo de error
            return render_to_response('filebrowser/createdir.html',
                                      {'repository': repository,
                                       'base_template': base_template,
                                       'path': path,
                                       'errornote': errornote,
                                       'url_prefix': url_prefix},
                                      context_instance=RequestContext(request))
        repository.create_dir(join(path, dirname))
        message = _('Folder created successfully')
        send_info(request, message)
        return HttpResponseRedirect(filebrowser_reverse(request, "filebrowser_dir_listing",
                        kwargs={'repository_name': repository.name,
                                'path': path},
                        url_prefix=url_prefix))
    else:
        dirs, files, parents, dirname = repository.list_directory(path)
        return render_to_response('filebrowser/createdir.html',
                                  {'repository': repository,
                                   'base_template': base_template,
                                   'path': path,
                                   'parents': parents,
                                   'url_prefix': url_prefix},
                                  context_instance=RequestContext(request))


@owner_or_superuser_required
def upload(request, repository_name, path='',
           base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    repository = get_object_or_404(Repository, name=repository_name)
    if request.method == 'POST':
        for k, f in request.FILES.items():
            if k.startswith('file_'):
                idx = k[5:]
                title = request.POST.get('title_' + idx).encode('utf8')
                description = request.POST.get('description_' + idx).encode('utf8')
                file_name = unicodedata.normalize('NFKD', force_unicode(f.name)).encode('ascii', 'ignore')
                fout = repository.create_file(join(path, file_name))
                for chunk in f.chunks():
                    fout.write(chunk)
                fout.close()
                metadata_name = join(path, file_name + '.metadata')
                metadata_path = repository.encode_path(repository.get_absolute_path(metadata_name))
                mout = open(metadata_path, 'w')
                mout.write(title)
                mout.write('\n\n')
                mout.write(description)
                mout.write('\n')
                mout.close()
        send_info(request, _('Files uploaded successfully'))
        return HttpResponseRedirect(filebrowser_reverse(request, "filebrowser_dir_listing",
                        kwargs={'repository_name': repository.name,
                                'path': path},
                        url_prefix=url_prefix))
    else:
        dirs, files, parents, dirname = repository.list_directory(path)
        return render_to_response('filebrowser/upload.html',
                                  {'repository': repository,
                                   'base_template': base_template,
                                   'path': path,
                                   'parents': parents,
                                   'url_prefix': url_prefix},
                                  context_instance=RequestContext(request))


def download(request, repository_name, path,
             base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    repository = get_object_or_404(Repository, name=repository_name)
    if not repository.check_file(path):
        raise Http404
    f = repository.get_file(path)
    mimetype = mimetypes.guess_type(repository.get_absolute_path(path))[0]
    if mimetype:
        return HttpResponse(f.read(), mimetype=mimetype)
    else:
        return HttpResponse(f.read())


@owner_or_superuser_required
def action(request, repository_name, path,
           base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    """ process rename, delete, etc. actions in files and directories """
    repository = get_object_or_404(Repository, name=repository_name)
    if 'renameform' in request.POST:
        action = 'confirmrename'
    elif 'deleteform' in request.POST:
        action = 'confirmdelete'
    elif 'rename' in request.POST:
        action = 'rename'
        old_elems = []
    else:
        action = 'delete'
    elems = []
    for k, v in request.POST.items():
        if (k.startswith('dir_') or k.startswith('file_') or
            k.startswith('elem_') or k.startswith('doc_')):
            if k.startswith('doc_'):
                try:
                    title = Document.objects.get(slug=v).title
                except:
                    title = v
                elems.append({'id': v, 'title': title})
            elif k.startswith('file_'):
                post_id = k[len('file_'):]
                new_file = {}
                new_file['id'] = v
                new_file['name'] = v
                new_file['title'] = request.POST.get('title_%s' % post_id, '').encode('utf8')
                new_file['description'] = request.POST.get('description_%s' % post_id, '').encode('utf8')
                elems.append(new_file)
            else:
                elems.append({'id': v, 'title': v})
            if action == 'rename':
                if k.startswith('dir_'):
                    old_elems.append(request.POST['olddir_%s' % k[len('dir_'):]])
                elif k.startswith('file_'):
                    old_elems.append(request.POST['oldfile_%s' % k[len('file_'):]])
                else:
                    old_elems.append(request.POST['olddoc_%s' % k[len('doc_'):]])
    if not elems:
        send_error(request, _("You didn't selected any element"))
        return HttpResponseRedirect(filebrowser_reverse(request, "filebrowser_dir_listing",
                        kwargs={'repository_name': repository.name,
                                'path': path},
                        url_prefix=url_prefix))
    if action in ['confirmrename', 'confirmdelete']:
        if action == 'confirmrename':
            template = 'filebrowser/rename.html'
        else:
            template = 'filebrowser/delete.html'
        basepath = repository.get_absolute_path(path)
        basepath = basepath.encode('utf-8').decode('utf-8')
        files = []
        dirs = []
        docs = []
        for e in elems:
            file = join(basepath, e['id'])
            if isdir(file):
                dirs.append(e)
            elif isfile(file):
                mfile = file + '.metadata'
                if exists(mfile):
                    mf = open(mfile, 'r')
                    mdata = mf.read()
                    mf.close()
                    mdata = mdata.split('\n\n')
                    e['title'] = mdata[0]
                    e['description'] = '\n\n'.join(mdata[1:])
                files.append(e)
            else:
                docs.append(e)
        pathdirs, pathfiles, parents, dirname = repository.list_directory(path)
        return render_to_response(template,
                                  {'repository': repository,
                                   'base_template': base_template,
                                   'path': path,
                                   'files': files,
                                   'parents': parents,
                                   'dirs': dirs,
                                   'docs': docs,
                                   'url_prefix': url_prefix,
                                  },
                                  context_instance=RequestContext(request))
    elif action == 'rename':
        repository.rename_elems(path, elems, old_elems)
        send_info(request, _('Elements renamed successfully'))
        return HttpResponseRedirect(filebrowser_reverse(request, "filebrowser_dir_listing",
                        kwargs={'repository_name': repository.name,
                                'path': path},
                        url_prefix=url_prefix))
    elif action == 'delete':
        repository.delete_elems(path, elems)
        send_info(request, _('Elements deleted successfully'))
        return HttpResponseRedirect(filebrowser_reverse(request, "filebrowser_dir_listing",
                        kwargs={'repository_name': repository.name,
                                'path': path},
                        url_prefix=url_prefix))
    else:
        return Http404


@owner_or_superuser_required
def createdoc(request, repository_name, path,
              base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    repository = get_object_or_404(Repository, name=repository_name)
    form = AddDocForm(request, repository=repository,
                      path=path, url_prefix=url_prefix)
    pathdirs, pathfiles, parents, dirname = repository.list_directory(path)
    return form.run(mode='add', repository=repository,
                    base_template=base_template, path=path,
                    parents=parents, url_prefix=url_prefix)


@owner_or_superuser_required
def editdoc(request, repository_name, doc_slug,
            base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    repository = get_object_or_404(Repository, name=repository_name)
    document = get_object_or_404(Document, repository=repository,
                                 slug=doc_slug)
    form = EditDocForm(request, document, repository=repository,
                       path=document.location, url_prefix=url_prefix)
    parents = document.get_parents()
    return form.run(mode='edit', repository=repository,
                    base_template=base_template, path=document.location,
                    doc_slug=doc_slug, parents=parents, url_prefix=url_prefix)


def viewdoc(request, repository_name, doc_slug,
            base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    repository = get_object_or_404(Repository, name=repository_name)
    document = get_object_or_404(Document, repository=repository,
                                    slug=doc_slug)
    file_field = None
    edit_permission = is_owner_or_superuser(request)
    if edit_permission and request.method == 'POST':
        if 'addfile' in request.POST:
            file_field = 'file'
            model_class = FileDocument
        elif 'addimage' in request.POST:
            file_field = 'image'
            model_class = ImageDocument

    if edit_permission and file_field and file_field in request.FILES:
        file = request.FILES[file_field]
        instance = model_class()
        instance.document = document
        instance.file.save(file.name, file)

    files = FileDocument.objects.filter(document=document)
    images = ImageDocument.objects.filter(document=document)
    parents = document.get_parents()

    return render_to_response('filebrowser/document.html',
                                {'repository': repository,
                                'base_template': base_template,
                                'parents': parents,
                                'document': document,
                                'doc_files': files,
                                'doc_images': images,
                                'edit_permission': edit_permission,
                                'url_prefix': url_prefix},
                                context_instance=RequestContext(request))


@owner_or_superuser_required
def remove_attachment(request, repository_name, type, objId,
                      base_template=FILEBROWSER_BASE_TEMPLATE, url_prefix=None):
    obj = None
    if type == 'file':
        obj = FileDocument.objects.get(id=objId)
    elif type == 'image':
        obj = ImageDocument.objects.get(id=objId)

    success = False
    if obj is not None:
        obj.delete()
        success = True

    json = simplejson.dumps({'success': success}, ensure_ascii=False)
    response = HttpResponse(json, '/text/javascript')
    response['X-JSON'] = json
    return response
