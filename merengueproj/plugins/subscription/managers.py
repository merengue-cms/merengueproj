from cmsutils.managers import ActiveManager

from merengue.base.managers import BaseContentManager


class SubscribableManager(ActiveManager, BaseContentManager):
    """ Show only published and not expired news items """

    def __init__(self):
        super(SubscribableManager, self).__init__(from_date='start_date', to_date='end_date')
