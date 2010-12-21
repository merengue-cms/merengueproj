# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

import popen2
import time

from django.forms.util import ErrorList, ValidationError
from django.utils.translation import ugettext_lazy as _

from merengue.base.forms import BaseAdminModelForm


class VideoCheckerModelForm(BaseAdminModelForm):

    def clean_file(self):
        value = self.cleaned_data.get('file', None)
        if not value or not value[0]:
            return value
        content = value[0]
        ffmpeg = "ffmpeg -i - -f null -"
        pop = popen2.Popen3(ffmpeg, capturestderr=False)
        chunks = content.chunks()
        time.sleep(1)
        while pop.poll() == -1:
            try:
                chunk = chunks.next()
                pop.tochild.write(chunk)
            except (StopIteration, IOError):
                pop.tochild.close()
                pop.fromchild.close()
        ffmpeg_exit_status = pop.wait()
        if ffmpeg_exit_status != 0:
            raise ValidationError(_('The file is not a video file or has a format not supported'))
        return value

    def clean(self):
        super(VideoCheckerModelForm, self).clean()
        file_cleaned_data, deleted_file = self.cleaned_data.get('file', [None, None])
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
        return self.cleaned_data
