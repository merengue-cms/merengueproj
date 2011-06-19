from merengue.base.admin import BaseContentAdmin
from merengue.section.admin import SectionContentAdmin


class FooModelAdmin(BaseContentAdmin):
    """ Admin for foo items """
    pass


class FooModelSectionAdmin(SectionContentAdmin, FooModelAdmin):
    """ Admin for foo items inside sections """
    manage_contents = True
