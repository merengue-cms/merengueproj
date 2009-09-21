from django.core.exceptions import ObjectDoesNotExist

from merengue.base.managers import WorkflowManager


class SectionManager(WorkflowManager):
    """ manager for all menu objects """

    def main(self):
        """ main menu """
        # XXX: for now, first menu will be main menu
        try:
            return self.all()[0]
        except IndexError:
            raise ObjectDoesNotExist()
