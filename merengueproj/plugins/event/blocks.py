from datetime import date

from django.utils.translation import ugettext as _

from merengue.registry import params
from merengue.block.blocks import Block

from plugins.event.utils import getEventsMonthYear


class EventsCalendarBlock(Block):
    name = 'eventscalendar'
    default_place = 'rightsidebar'


    config_params = [params.Single(name='calendar_tooltip_color', label=_('calendar tooltip color'), default='black')]

    @classmethod
    def render(cls, request, place):
        calendar_tooltip_color = cls.get_config()['calendar_tooltip_color'].get_value()

        current_month = date.today().month
        current_year = date.today().year
        events_dic = getEventsMonthYear(current_month, current_year)
        return cls.render_block(request,
                                template_name='event/block_calendar.html',
                                block_title=_('Events calendar'),
                                context={'events_dic': events_dic,
                                         'calendar_tooltip_color': calendar_tooltip_color})
