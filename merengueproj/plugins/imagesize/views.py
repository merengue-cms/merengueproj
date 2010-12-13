# Copyright (c) 2010 by Yaco Sistemas <dgarcia@yaco.es>
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

import os
import datetime
from PIL import Image

from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.utils.translation import ugettext as _

from plugins.imagesize.models import ImageSize


def imagesize(request):
    notify()
    return HttpResponse('<xml>OK</xml>')


def notify():
    bigimages = {}
    for imagesize in ImageSize.objects.all():
        width = imagesize.max_width
        height = imagesize.max_height
        dirpath = os.path.join(settings.MEDIA_ROOT, imagesize.folder)
        for path in os.listdir(dirpath):
            fullpath = os.path.join(dirpath, path)
            try:
                img = Image.open(fullpath)
                w, h = img.size
                imgstr = '%s (%sx%s)' % (path, w, h)
                if w > width or h > height:
                    bigimages[imagesize] = bigimages.get(imagesize, []) +\
                                           [imgstr]
            except IOError:
                pass

    now = datetime.datetime.now()
    # 3 days between notifications
    timedelta = now - datetime.timedelta(3)
    for imagesize in bigimages:
        if imagesize.notified and imagesize.notified > timedelta:
            continue

        to_mail = map(unicode.strip, imagesize.recipients.split(','))
        subject = _('Images bigger than expected in %(folder)s') %\
                    dict(folder=imagesize.folder)
        msg = _('''There are images bigger than expected in %(folder)s.
The max size is setted to %(width)s x %(height)s.

''') % dict(folder=imagesize.folder,
           width=imagesize.max_width,
           height=imagesize.max_height)

        msg += '\n'.join(' * ' + img for img in bigimages[imagesize])
        email = EmailMessage(subject, msg, settings.DEFAULT_FROM_EMAIL,
                             to_mail)
        email.send()
        imagesize.notified = datetime.datetime.now()
        imagesize.save()
