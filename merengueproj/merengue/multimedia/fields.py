# -*- coding: utf-8 -*-
import os
import re
import subprocess
import tempfile
import time

from django.conf import settings
from django.core.files import File
from django.core.files.images import ImageFile
from django.db import models

from stdfile.db.fields import RemovableFileField

from merengue.utils import bin_exists


class VideoException(Exception):
    pass


class VideoFile(File):
    """
    A mixin for use alongside django.core.files.base.File, which provides
    additional features for dealing with videos.
    """

    def _get_thumbnail(self):
        thumbnail_name = re.sub('%s$' % self.field.codec, 'jpg', self.name)
        os.chdir(settings.MEDIA_ROOT)
        if os.path.exists(thumbnail_name):
            thumbnail_file = open(thumbnail_name, 'rw')
            return ImageFile(thumbnail_file)
        else:
            return None
    thumbnail = property(_get_thumbnail)


duration_re = re.compile(r"Duration: (?P<hours>[0-9][0-9]):"
                         r"(?P<minutes>[0-9][0-9]):"
                         r"(?P<seconds>[0-9][0-9])\.[0-9][0-9]?")


class AutoEncodeFieldFile(VideoFile, models.fields.files.FieldFile):

    def save(self, name, content, save=True):
        try:
            dot_index = name.rindex('.')
        except ValueError:  # filename has no dot
            pass
        else:
            name = name[:dot_index]
        # Encode video
        duration = self.encode_video(content, name, codec=self.field.codec,
                                     max_width=self.field.max_width,
                                     max_height=self.field.max_height)
        if self.field.duration_field:
            setattr(self.instance, self.field.duration_field, duration)
        new_filename = '%s.%s' % (name, self.field.codec)
        super(AutoEncodeFieldFile, self).save(new_filename, content, save)

    def delete(self, save=True):
        if self.thumbnail and os.path.exists(self.thumbnail.name):
            os.remove(self.thumbnail.name)
        super(AutoEncodeFieldFile, self).delete(save)

    def encode_video(self, content, name,
                     max_width=None, max_height=None, codec=None):
        """
        Resize and encode a video. Requires ffmpeg and yamdi.
        """
        import popen2
        if codec is None:
            codec = 'flv'
        tempfd, tempfilename = tempfile.mkstemp()
        os.close(tempfd)
        ffmpeg = "ffmpeg -y -i - -acodec libmp3lame -ar 22050 -ab 96k " \
                 "-f %s -s %dx%d %s -b 900000" % (codec,
                                                  (max_width or 320),
                                                  (max_height or 240),
                                                  tempfilename)
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
            raise VideoException(ffmpeg_exit_status)
        if codec == 'flv' and bin_exists('yamdi'):
            # inject FLV metadata
            tempfd2, tempfilename2 = tempfile.mkstemp()
            os.close(tempfd2)
            yamdi = "yamdi -i %s -o %s" % (tempfilename, tempfilename2)
            os.popen(yamdi)
            os.rename(tempfilename2, tempfilename)
        vf = open(tempfilename)
        content._file.seek(0)
        content._file.write(vf.read())
        content._file.truncate()
        vf.close()
        fin, fout, ferr = os.popen3("ffmpeg -i %s" % tempfilename)
        video_info = ferr.read()
        fin.close()
        fout.close()
        ferr.close()
        match = duration_re.search(video_info)
        if match:
            duration_seconds = (int(match.groupdict()['seconds']) +
                                int(match.groupdict()['minutes']) * 60 +
                                int(match.groupdict()['hours']) * 3600)
        else:
            duration_seconds = 0
        filename = "%s.%s" % (name, codec)
        video_path = self.field.generate_filename(self.instance, filename)
        video_path = self.storage.get_available_name(video_path)
        video_path = os.path.join(settings.MEDIA_ROOT, video_path)
        thumbnail_path = re.sub('%s$' % codec, 'jpg', video_path)
        ffmpeg_thumbnail = 'ffmpeg -y -itsoffset -%d -i %s -vcodec mjpeg ' \
                           '-vframes 1 -an -f rawvideo -s %dx%d %s' % \
                           (duration_seconds / 2, tempfilename,
                           (max_width or 320), (max_height or 240),
                           thumbnail_path)
        subprocess.call(ffmpeg_thumbnail.split(' '))
        os.remove(tempfilename)
        return duration_seconds


class VideoField(RemovableFileField):
    """FileField that automatically resizes and encodes uploaded videos."""
    attr_class = AutoEncodeFieldFile

    def __init__(self, *args, **kwargs):
        self.max_width = kwargs.pop('max_width', None)
        self.max_height = kwargs.pop('max_height', None)
        self.codec = kwargs.pop('codec', None)
        self.duration_field = kwargs.pop('duration_field', None)
        super(VideoField, self).__init__(*args, **kwargs)
