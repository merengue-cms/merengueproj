from datetime import date

# from django.db.models import Q
from django.utils.translation import ugettext as _

from merengue.block.blocks import Block
from plugins.event.models import Occurrence


class EventsCalendarBlock(Block):
    name = 'eventscalendar'
    default_place = 'rightsidebar'

    @classmethod
    def render(cls, request, place):
        current_month = date.today().month
        filters = (
            #Q(start__month=current_month) | Q(end__month=current_month),
        )
        events_list = Occurrence.objects.all().filter(*filters)
        return cls.render_block(request,
                                template_name='event/block_calendar.html',
                                block_title=_('Events calendar'),
                                context={'events_list': events_list})
