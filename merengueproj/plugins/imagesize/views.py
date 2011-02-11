# encoding: utf-8
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

import os
import datetime
try:
    from PIL import Image
except ImportError:
    import Image  # pyflakes:ignore

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from notification import models as notification

from merengue.multimedia.models import Photo
from plugins.imagesize.models import ImageSize


def imagesize(request):
    notify()
    return HttpResponse('<xml>OK</xml>')


def notify():
    bigimages = {}
    broken_dirs = {}
    for imagesize in ImageSize.objects.all():
        width = imagesize.max_width
        height = imagesize.max_height
        dirpath = os.path.join(settings.MEDIA_ROOT, imagesize.folder)
        try:
            paths = os.listdir(dirpath)
        except OSError:
            broken_dirs[imagesize] = dirpath
            continue
        for path in paths:
            fullpath = os.path.join(dirpath, path)
            try:
                img = Image.open(fullpath)
                w, h = img.size
                imgstr = u'%s (%sx%s)' % (path, w, h)
                try:
                    photo = Photo.objects.get(
                        image=os.path.join(imagesize.folder, path))
                    if photo.multimediarelation_set.count():
                        imgstr = u''
                        for content_rel in photo.multimediarelation_set.all():
                            content_path = content_rel.content.get_real_instance().public_link()
                            image_path = photo.image.url
                            domain = 'http://%s' % Site.objects.all()[0].domain
                            content_url = '%s%s' % (domain, content_path)
                            image_url = '%s%s' % (domain, image_path)
                            imgstr += u'%s en el contenido %s con dimensiones (%sx%s)' % (image_url,
                                                                                          content_url,
                                                                                          w, h)
                except Photo.DoesNotExist:
                    pass
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

        subject = _("Images bigger than expected in '%(folder)s'") %\
                    dict(folder=imagesize.folder)
        msg = _('''There are images bigger than expected in '%(folder)s'.
The max size is setted to %(width)s x %(height)s.

''') % dict(folder=imagesize.folder,
           width=imagesize.max_width,
           height=imagesize.max_height)

        msg += '\n'.join(' * ' + img for img in bigimages[imagesize])
        context = dict(subject=subject, msg=msg)
        notification.send(imagesize.recipients.all(), 'imagesize_images', context)
        imagesize.notified = datetime.datetime.now()
        imagesize.save()

    if broken_dirs:
        for imagesize, broken in broken_dirs.items():
            if imagesize.notified and imagesize.notified > timedelta:
                continue
            subject = _("Can't open directory '%(folder)s'") %\
                      dict(folder=imagesize.folder)
            msg = _("Can't check image size in folder '%(folder)s'\n") %\
                      dict(folder=imagesize.folder)
            context = dict(subject=subject, msg=msg)
            notification.send(imagesize.recipients.all(), 'imagesize_broken', context)

            imagesize.notified = datetime.datetime.now()
            imagesize.save()
