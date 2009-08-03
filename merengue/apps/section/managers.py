from base.managers import BaseManager


class WorkflowManagerDocument(BaseManager):
    """ manager for all objects that have a workflow (a status field) """

    def by_status(self, status):
        return self.filter(status=status)

    def draft(self):
        """ only draft objects """
        return self.by_status(1)

    def published(self):
        """ only published objects """
        return self.by_status(2)
