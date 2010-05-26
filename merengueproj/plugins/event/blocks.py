from datetime import date

from django.utils.translation import ugettext as _

from merengue.block.blocks import Block

from plugins.event.utils import getEventsMonthYear


class EventsCalendarBlock(Block):
    name = 'eventscalendar'
    default_place = 'rightsidebar'

    @classmethod
    def render(cls, request, place, context, *args, **kwargs):
        current_month = date.today().month
        current_year = date.today().year
        events_dic = getEventsMonthYear(current_month, current_year)
        return cls.render_block(request,
                                template_name='event/block_calendar.html',
                                block_title=_('Events calendar'),
                                context={'events_dic': events_dic})
