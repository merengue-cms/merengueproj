from django.contrib.admin.widgets import AdminFileWidget
from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings

try:
    from PIL import Image
except ImportError:
    import Image  # pyflakes:ignore
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO   # pyflakes:ignore

from stdimage.globals import DELETED


class DelAdminFileWidget(AdminFileWidget):
    '''
    A AdminFileWidget that shows a delete checkbox
    '''
    input_type = 'file'

    def render(self, name, value, attrs=None):
        from stdimage.fields import StdImageFieldFile
        input = super(forms.widgets.FileInput, self).render(name, value, attrs)
        if value and value != DELETED and isinstance(value, StdImageFieldFile):
            item = '<tr><td style="vertical-align: middle;">%s</td><td>%s</td>'
            output = []
            output.append('<table style="border-style: none;">')
            output.append(item % (_('Currently:'), '<a target="_blank" href="%s%s">%s</a>' % (settings.MEDIA_URL, value, value)))
            output.append(item % (_('Change:'), input))
            try:
                if hasattr(value, 'temporary_file_path'):
                    file = value.temporary_file_path()
                else:
                    if 'read' in dir(value):
                        file = StringIO(value.read())
                    else:
                        file = StringIO(value['content'])
                Image.open(file)
                output.append(item % (_('Delete') + ':', '<input type="checkbox" name="%s_delete"/>' % name))  # split colon to force "Delete" that is already translated
            except IOError:
                pass
            output.append('</table>')
            return mark_safe(u''.join(output))
        else:
            return mark_safe(input)

    def value_from_datadict(self, data, files, name):
        if not data.get('%s_delete' % name):
            return super(DelAdminFileWidget, self).value_from_datadict(data, files, name)
        else:
            return DELETED
