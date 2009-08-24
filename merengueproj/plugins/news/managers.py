from cmsutils.managers import ActiveManager

from merengue.base.managers import BaseContentManager


class NewsItemManager(ActiveManager, BaseContentManager):
    """ Show only published and not expired news items """

    def __init__(self):
        super(NewsItemManager, self).__init__(from_date='publish_date', to_date='expire_date')

    def actives(self):
        return super(NewsItemManager, self).actives().filter(status='published')

    def allpublished(self):
        return self.filter(status='published')

    def published(self):
        return self.actives().filter(status='published')
