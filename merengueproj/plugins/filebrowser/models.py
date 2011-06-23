# -*- coding: utf-8 -*-
import os
import shutil

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext_lazy as _

from merengue.base.dbfields import AutoSlugField
from merengue.section.models import BaseSection

from plugins.filebrowser.managers import (RepositoryManager, DocumentManager,
                                          FileDocumentManager)
from plugins.filebrowser.storage import (FileBrowserStorage,
                                         get_root_location, get_location,
                                         get_base_url)
from plugins.filebrowser.utils import FileDesc, DirDesc


doc_storage = FileBrowserStorage(location=get_location, base_url=get_base_url)


def get_upload_dir(instance, name):
    return '%s/%s' % (instance.document.id, name)


class Repository(models.Model):
    """ Repository model """
    name = models.SlugField(_(u'name'), max_length=200, unique=True)
    section = models.ForeignKey(BaseSection, null=True, blank=True)

    objects = RepositoryManager()

    class Meta:
        ordering = ('name', )
        verbose_name = _(u'repository')
        verbose_name_plural = _(u'repositories')

    def __init__(self, *args, **kwargs):
        super(Repository, self).__init__(*args, **kwargs)
        self.rebuild_if_missing()

    def __unicode__(self):
        return _(u'Repository at %s') % self.get_root_path()

    def get_absolute_url_with_out_section(self):
        return reverse('filebrowser_root', args=(self.name, ))

    def get_absolute_url(self):
        url_with_out_section = self.get_absolute_url_with_out_section()
        if self.section:
            return self.section.get_real_instance().url_in_section(url_with_out_section)
        return url_with_out_section

    def save(self, force_insert=False, force_update=False):
        super(Repository, self).save(force_insert, force_update)
        self.rebuild_if_missing()

    def rebuild_if_missing(self):
        if not os.path.exists(get_root_location()):
            os.mkdir(get_root_location())
        if not os.path.exists(self.get_root_path()):
            os.mkdir(self.get_root_path())

    def encode_path(self, path):
        assert(isinstance(path, unicode))
        abspath = self.get_absolute_path(path)
        abspath = abspath.encode('utf-8')
        return abspath

    def get_root_path(self):
        return os.path.join(get_root_location(), force_unicode(self.name))

    def get_absolute_path(self, path):
        return os.path.join(self.get_root_path(), force_unicode(path))

    def check_dir(self, path):
        path = self.encode_path(path)
        return os.path.isdir(path)

    def check_file(self, path):
        path = self.encode_path(path)
        return os.path.isfile(path)

    def list_directory(self, path):
        dirs = []
        files = []
        path = smart_str(path)
        root_path = smart_str(self.get_root_path())
        absolute_path = smart_str(self.get_absolute_path(path))
        for l in os.listdir(absolute_path):
            fullpath = os.path.join(absolute_path, l)
            if l.startswith('.'):
                continue  # is hidden
            if os.path.isdir(fullpath):
                item_path = os.path.join(path, l)
                desc = DirDesc(root_path, item_path)
                if item_path.endswith('/'):
                    location = item_path
                else:
                    location = item_path + '/'
                desc.childnumber += Document.objects.filter(location=location).count()
                dirs.append(desc)
            elif os.path.isfile(fullpath):
                files.append(FileDesc(root_path, os.path.join(path, l)))
        parents = []
        p, lastdir = os.path.split(path)
        while p:
            dirpath = p
            p, dirname = os.path.split(p)
            parents.insert(0, {'dirname': dirname, 'path': dirpath})
        return dirs, files, parents, lastdir

    def create_dir(self, dir_path):
        path = self.encode_path(dir_path)
        os.makedirs(path)

    def create_file(self, file_path):
        path = self.encode_path(self.get_absolute_path(file_path))
        return open(path, 'wb+')

    def get_file(self, file_path):
        path = self.encode_path(self.get_absolute_path(file_path))
        return open(path)

    def rename_elems(self, path, elems, old_elems):
        basepath = self.get_absolute_path(path)
        for i, elem in enumerate(elems):
            oldfile = os.path.join(basepath, old_elems[i])
            newfile = os.path.join(basepath, elem['id'])
            if oldfile != newfile:
                if os.path.exists(oldfile):
                    shutil.move(oldfile, newfile)
                else:
                    doc = self.document_set.get(slug=old_elems[i])
                    doc.title = elem['title']
                    doc.save()

    def delete_elems(self, path, elems):
        basepath = self.get_absolute_path(path)
        for elem in elems:
            file = os.path.join(basepath, elem['id'])
            if os.path.isdir(file):
                shutil.rmtree(file)
            elif os.path.isfile(file):
                os.remove(file)
            else:
                # it should be a document
                doc = self.document_set.get(repository=self, slug=elem['id'])
                doc.delete()


class Document(models.Model):
    """ Document model """
    repository = models.ForeignKey(Repository)
    slug = AutoSlugField(autofromfield='title', max_length=200)
    title = models.CharField(_(u'title'), max_length=150)
    content = models.TextField(_(u'content'))
    modification_date = models.DateField(_(u'modification date'),
        auto_now=True, editable=False)
    location = models.CharField(_(u'location'), max_length=200,
        null=False, blank=False, default='/')
    objects = DocumentManager()

    class Meta:
        verbose_name = _(u'document')
        verbose_name_plural = _(u'documents')

    def __unicode__(self):
        return u'%s%s' % (self.location, self.slug)

    def get_absolute_url(self):
        return self.location

    def get_size(self):
        return len(self.content)

    def get_parents(self):
        parents = []
        p, lastdir = os.path.split(self.location)
        while p and p != '/':
            dirpath = p
            p, dirname = os.path.split(p)
            parents.insert(0, {'dirname': dirname, 'path': dirpath})
        return parents

    def save(self):
        super(Document, self).save()
        basedir = os.path.join(get_location(), str(self.id))
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        location = os.path.join(self.repository.get_root_path(), self.location)
        if not os.path.exists(location):
            os.makedirs(location)

    def delete(self):
        basedir = os.path.join(get_location(), str(self.id))
        super(Document, self).delete()
        if os.path.exists(basedir):
            shutil.rmtree(basedir)


class FileDocument(models.Model):
    """ An attachment for a document """
    document = models.ForeignKey(Document, verbose_name=_(u'document'))
    file = models.FileField(_(u'file'), upload_to=get_upload_dir,
        storage=doc_storage, null=False, blank=False)
    indexed = models.BooleanField(_(u'indexed'), default=False, editable=False)
    objects = FileDocumentManager()

    class Meta:
        verbose_name = _(u'document file attachment')
        verbose_name_plural = _(u'document file attachments')

    def get_absolute_url(self):
        return self.document.get_absolute_url()

    def get_class(self):
        return self.__class__.__name__.lower()

    def save(self, reset_index=True, *args, **kwargs):
        if reset_index:
            self.indexed = False
        return super(FileDocument, self).save(*args, **kwargs)


class ImageDocument(models.Model):
    """ An image for a document """
    document = models.ForeignKey(Document, verbose_name=_(u'document'))
    file = models.ImageField(_(u'file'), upload_to=get_upload_dir,
        storage=doc_storage, null=False, blank=False)

    class Meta:
        verbose_name = _(u'document image attachment')
        verbose_name_plural = _(u'document image attachments')

    def get_absolute_url(self):
        return self.document.get_absolute_url()
