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

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from merengue.action.actions import ContentAction, SiteAction
from merengue.section.utils import get_section


class BaseGenerateRSS(object):

    def get_url_to_rss(self, request):
        return reverse('rss_views')

    def get_response(self, request):
        return HttpResponseRedirect(self.get_url_to_rss(request))


class GenerateRSS(BaseGenerateRSS, SiteAction):
    name = 'generaterss'
    verbose_name = _('Generate RSS feed')
    help_text = _('Creates the rss feed')


class GenerateSectionRSS(BaseGenerateRSS, ContentAction):
    name = 'generatesectionrss'
    verbose_name = _('Generate Section RSS feed')
    help_text = _('Creates the rss feed from a section')
    active_by_default = False

    def has_action(self, request, content):
        return super(GenerateSectionRSS, self).has_action(request, content) and get_section(request)

    def get_response(self, request, content):
        url_base = self.get_url_to_rss(request)
        sections = content.sections.all()
        if sections:
            url = "%s?sections__in=%d" % (url_base, sections[0].pk)
        else:
            url = url_base
        return HttpResponseRedirect(url)
