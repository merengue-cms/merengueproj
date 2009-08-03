import tempfile
from os import path

from django import forms
from django.forms.util import ErrorList
from django.conf import settings
from django.template.loader import render_to_string

from rosetta import polib, poutil


PO_PROJECT_BASE = 'po_project_base'


class FormAdminDjango(forms.Form):

    def as_django_admin(self):
        return render_to_string('rosetta/form_admin_django.html', {'form': self, })


class UpdateConfirmationPoForm(FormAdminDjango):
    pass


class UpdatePoForm(FormAdminDjango):
    priority = forms.BooleanField(required=False)
    file = forms.FileField()

    def __init__(self, pofile, *args, **kwargs):
        super(UpdatePoForm, self).__init__(*args, **kwargs)
        self.fields['priority'].is_checkbox = True
        self.data_file = None
        self.pofile = pofile
        if not pofile:
            application_choices = self._get_application_choices()
            self.fields['application'] = forms.ChoiceField(choices=application_choices, required=False)

            language_choices = [('', '-----')]
            if hasattr(settings, 'LANGUAGES'):
                language_choices.extend([(key, "%s (%s)" %(value, key)) \
                                        for key, value in dict(settings.LANGUAGES).items()])
            self.fields['language'] = forms.ChoiceField(choices=language_choices, required=False)
            self.fields.keyOrder = ['application', 'language', 'priority', 'file']

    def clean(self):
        cleaned_data = super(UpdatePoForm, self).clean()
        if not self.errors and not self.pofile:
            try:
                tmp_file, po_tmp, po_dest_file = self._get_files_to_merge()
                tmp_file.close()
            except IOError:
                file_error = self._errors.get('file', ErrorList([]))
                file_error_new = ErrorList([u'Information incompatible for find the destination file'])
                file_error.extend(file_error_new)
                self._errors['file'] = ErrorList(file_error)
        return cleaned_data

    def save_temporal_file(self):
        tmp_file, po_tmp, po_dest_file = self._get_files_to_merge()
        tmp_file.flush()
        return po_tmp, po_dest_file, self.cleaned_data['priority']

    def _get_files_to_merge(self):
        # Escribo el archivo que ha mandado el usuario en un archivo temporal
        temporal_filepath = tempfile.NamedTemporaryFile().name
        tmp_file = open(temporal_filepath, "w")

        if self.data_file is None:
            self.data_file = self.cleaned_data['file'].read()
        tmp_file.write(self.data_file)
        tmp_file.flush()
        po_tmp = polib.pofile(temporal_filepath)

        if not self.pofile:
            # Consigo la ruta del archivo con el cual voy a hacer un merge, creo un pofile
            path_file = _get_path_file(po_tmp, self.cleaned_data['file'].name,
                        self.cleaned_data.get('language', None),
                        self.cleaned_data.get('application', None))
            po_dest_file = polib.pofile(path_file)
        else:
            po_dest_file = self.pofile
        return (tmp_file, po_tmp, po_dest_file)

    def _get_application_choices(self):
        l = []
        choices = [('', '-----')]
        for language in settings.LANGUAGES:
            l_extend = poutil.find_pos(language[0], include_djangos=False, include_rosetta=False)
            l_extend = [item.split(settings.BASEDIR)[1] for item in l_extend]
            l.extend(l_extend)
        for item in l:
            item_split = item.split('/')
            if item_split[1] == 'locale':
                if not (PO_PROJECT_BASE, 'entire project') in choices:
                    choices.append((PO_PROJECT_BASE, 'entire project'))
            else:
                item_split2 = item.split("/locale/")
                item_tuple = (item_split2[0][1:], item_split2[0].split('/')[-1])
                if not item_tuple in choices:
                    choices.append(item_tuple)
        return choices


def _get_lang(lang, lang_cleaned_data=None):
    if lang_cleaned_data:
        return lang_cleaned_data
    lang = lang.replace('\n', '')
    lang = lang.strip()
    lang_words = lang.split(' ')
    if len(lang_words):
        lang = lang_words[0]
    return lang.lower()


def _get_lang_by_file(file_path):
    cut_start = "locale/"
    cut_end = "/LC_MESSAGES"
    index_start = file_path.index(cut_start) + len(cut_start)
    index_end = file_path.index(cut_end)
    return file_path[index_start:index_end]


def _get_application(application, application_cleaned_data=None):
    if application_cleaned_data:
        app = application_cleaned_data
        if app != PO_PROJECT_BASE:
            return app
        else:
            return ''

    application = application.replace('\n', '')
    application = application.strip()
    return application.lower()


def _get_path_file(po_tmp, filename, lang=None, application=None):
    lang = _get_lang(po_tmp.metadata.get('Language-Team'), lang)
    directory = _get_application(po_tmp.metadata.get('Project-Id-Version'), application)
    return path.join(settings.BASEDIR, directory, 'locale', lang, 'LC_MESSAGES', filename)
