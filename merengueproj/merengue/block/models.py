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

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from merengue.base.models import BaseContent
from merengue.registry.managers import RegisteredItemManager
from merengue.registry.models import RegisteredItem

import re


PLACES = (('all', _('All')),
          ('leftsidebar', _('Left sidebar')),
          ('rightsidebar', _('Right sidebar')),
          ('aftercontenttitle', _('After content title')),
          ('beforecontent', _('Before content body')),
          ('homepage', _('Home page')),
          ('aftercontent', _('After content body')),
          ('header', _('Header')),
          ('footer', _('Footer')),
          ('meta', _('Meta-information, links, js...')))


class RegisteredBlock(RegisteredItem):
    name = models.CharField(_('name'), max_length=100)
    placed_at = models.CharField(_('placed at'), max_length=100, choices=PLACES)
    shown_in_urls = models.TextField(
        _('shown in urls'),
        blank=True,
        help_text=_("""block will <em>only</em> be visible in urls matching these
            regular expressions (one per line, using <a\
            href='http://docs.python.org./library/re.html#regular-expression-syntax'
            title='python regular expressions' target='_blank'>python re syntax</a>). <br/>
            Please use relative paths.
            This field has preference over 'hidden in urls'."""))
    hidden_in_urls = models.TextField(
        _('hidden in urls'),
        blank=True,
        help_text=_("""block will be hidden in urls matching these regular
            expressions (one per line, using <a
            href='http://docs.python.org/library/re.html#regular-expression-syntax'
            title='python regular expressions' target='_blank'>python re syntax</a>)."""))
    is_fixed = models.BooleanField(
        verbose_name=_('disable the activation and desactivation of the block'),
        default=False)
    # fields for blocks related to contents
    content = models.ForeignKey(BaseContent, verbose_name=_(u'related content'), null=True)
    overwrite_if_place = models.BooleanField(
        verbose_name=_('overwrite block if the place is the same'),
        default=True)
    overwrite_always = models.BooleanField(
        verbose_name=_('overwrite generic block if is present on the actual page'),
        default=False)

    objects = RegisteredItemManager()

    def show_in_url(self, url):

        def _matches(url, exp):
            for e in exp:
                try:
                    urlre = re.compile(e, re.IGNORECASE)
                    if urlre.search(url):
                        return True
                except re.error, err:  # pyflakes:ignore
                    continue
            return False

        if self.shown_in_urls:
            return _matches(url, self.shown_in_urls.split())
        elif self.hidden_in_urls:
            return not _matches(url, self.hidden_in_urls.split())
        else:
            return True

    def print_block(self, placed_at, url):
        if self.placed_at in ['all', placed_at]:
            return self.show_in_url(url)
        return False

    def __unicode__(self):
        return self.name


def post_save_handler(sender, instance, **kwargs):
    content = instance.content
    if content and not content.has_related_blocks:
        # we mark that base content has related blocks, for performance reason
        content.has_related_blocks = True
        content.save()


def pre_delete_handler(sender, instance, **kwargs):
    content = instance.content
    if content:
        other_content_blocks = RegisteredBlock.objects.filter(content=content).exclude(pk=instance.pk)
        if not other_content_blocks:
            # we unmark that base content has relateds block
            content.has_related_blocks = False
            content.save()


signals.post_save.connect(post_save_handler, sender=RegisteredBlock)
signals.pre_delete.connect(pre_delete_handler, sender=RegisteredBlock)
