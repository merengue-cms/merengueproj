from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from merengue.base.forms import BaseAdminModelForm


class VideoCheckerModelForm(BaseAdminModelForm):

    def clean(self):
        super(VideoCheckerModelForm, self).clean()
        file_cleaned_data, deleted_file = self.cleaned_data.get('file', None)
        url_cleaned_data = self.cleaned_data.get('external_url', None)
        old_file = self.instance and self.instance.file
        if not old_file and not url_cleaned_data and not file_cleaned_data:
            global_errors = self.errors.get('__all__', ErrorList([]))
            global_errors.extend(ErrorList([_(u'Please specify at least a video file or a video url')]))
            self._errors['__all__'] = ErrorList(global_errors)
        elif deleted_file and not url_cleaned_data:
            global_errors = self.errors.get('__all__', ErrorList([]))
            global_errors.extend(ErrorList([_(u'If you want to remove the file, you can specify a video url')]))
            self._errors['__all__'] = ErrorList(global_errors)
        elif file_cleaned_data:
            extension = file_cleaned_data.name.split('.')[-1].lower()
            if extension not in ('flv', 'f4v'):
                file_errors = self.errors.get('file', ErrorList([]))
                file_errors.extend(ErrorList([_(u'Video file must be in flv format')]))
                self._errors['file'] = ErrorList(file_errors)
        return self.cleaned_data
