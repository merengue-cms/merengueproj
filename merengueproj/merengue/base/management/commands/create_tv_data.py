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

# -*- coding: utf-8 -*-
from optparse import make_option
import datetime
import os
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from transmeta import get_fallback_fieldname


class Command(BaseCommand):
    help = (u"Create example tv contents")
    option_list = BaseCommand.option_list + (
        make_option('-d', '--directory', default='', dest='directory',
                    help='Directory that contains preview files'),
                   )

    channels = [('Canal Yaco', 'canal-yaco', ),
                ('Canal Yaco+', 'canal-yaco-plus', ),
               ]
    video_ids = [('flv_8cca5ea9-fd05-4406-b0e0-bf1808cbae1e', 'Yaco es así', 294),
                 ('flv_ef2672ff-10cd-4f71-8fb2-a2415609faf4', 'Compra en Pilas', 165),
                ]
    livestream_channel = 'yacontents'
    preview_images = ['01.jpg', '02.jpg', '03.jpg', '04.jpg', '05.jpg', '06.jpg', '07.jpg',
                      '08.jpg', '09.jpg', '10.jpg']

    def createChannels(self):
        from plugins.tv.models import Channel

        print "Creating channels...",
        for name, slug in self.channels:
            (channel, created) = Channel.objects.get_or_create(slug=slug)
            if created:
                setattr(channel, get_fallback_fieldname('name'), name)
                channel.status = 'published'
                channel.save()
        print "DONE"

    def createVideoStreamings(self):
        from plugins.tv.models import VideoStreaming

        print "Creating videostreamings...",
        for id, name, duration in self.video_ids:
            (vstream, created) = VideoStreaming.objects.get_or_create(clip_id = id)
            if created:
                vstream.duration = duration
                vstream.name = name
                vstream.status = 'published'
                vstream.channel = self.livestream_channel
                preview = os.path.join(self.imagedir, random.choice(self.preview_images))
                if os.path.exists(preview):
                    file = open(preview)
                    filename = os.path.basename(preview)
                    vstream.preview.save(filename, ContentFile(file.read()))
                    file.close()
                    vstream.save()
                    vstream.preview.field._force_create_thumbnail(instance=vstream)
                else:
                    vstream.save()

        print "DONE"

    def createSchedules(self):
        from plugins.tv.models import Schedule, VideoStreaming, Channel

        print "Creating schedules...",
        now = datetime.datetime.now()
        videos = list(VideoStreaming.objects.all())
        channels = list(Channel.objects.all())

        for i in range(40):
            now += datetime.timedelta(minutes=random.randint(30, 240))
            video = random.choice(videos)
            channel = random.choice(channels)
            (schedule, created) = Schedule.objects.get_or_create(broadcast_date=now,
                                                                 channel=channel,
                                                                 video=video)

        print "DONE"

    def handle(self, *args, **options):
        directory = options.get('directory', '')
        if not directory or not os.path.exists(directory) or not os.path.isdir(directory):
            self.imagedir = None
        else:
            self.imagedir = directory

        self.createChannels()
        self.createVideoStreamings()
        self.createSchedules()
