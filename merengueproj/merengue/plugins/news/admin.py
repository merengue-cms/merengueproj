from merengue.base.admin import BaseCategoryAdmin, BaseContentAdmin
from merengue.section.admin import SectionContentAdmin
from plugins.news.models import NewsItem, NewsCategory


class NewsCategoryAdmin(BaseCategoryAdmin):
    pass


class NewsItemAdmin(BaseContentAdmin):
    list_filter = BaseContentAdmin.list_filter + ('categories', )
    html_fields = BaseContentAdmin.html_fields + ('body', )

    class Media:
        js = ('news/date_auto_fill.js', )


class NewsItemSectionAdmin(NewsItemAdmin, SectionContentAdmin):
    pass


def register(site):
    """ Merengue admin registration callback """
    site.register(NewsCategory, NewsCategoryAdmin)
    site.register(NewsItem, NewsItemAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(NewsCategory)
    site.unregister(NewsItem)
