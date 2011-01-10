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

from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from merengue.base.forms import BaseAdminModelForm
from plugins.voting.models import get_min_score, get_max_score


class VoteForm(BaseAdminModelForm):

    def clean(self):
        cleaned_data = super(VoteForm, self).clean()
        vote = cleaned_data.get('vote', None)
        if vote is not None and (vote > get_max_score() or vote < get_min_score()):
            vote_error = self._errors.get('vote', ErrorList([]))
            vote_error_new = ErrorList([_(u'The vote have to be Between %(min_score)s and %(max_score)s' % {'min_score': get_min_score(),
                                                                                                            'max_score': get_max_score()})])
            vote_error.extend(vote_error_new)
            self._errors['vote'] = ErrorList(vote_error)
        return cleaned_data

    def save(self, *args, **kwargs):
        vote = super(VoteForm, self).save(*args, **kwargs)
        vote.num_votes = self.cleaned_data['users'].count()
        return vote
