from base.admin import BaseCategoryAdmin, BaseContentAdmin
from plugins.news.models import NewsItem, NewsCategory


class NewsCategoryAdmin(BaseCategoryAdmin):
    pass


class NewsItemAdmin(BaseContentAdmin):
    list_filter = BaseContentAdmin.list_filter + ('categories', )
    html_fields = BaseContentAdmin.html_fields + ('body', )


def register(site):
    """ Merengue admin registration callback """
    site.register(NewsCategory, NewsCategoryAdmin)
    site.register(NewsItem, NewsItemAdmin)


def unregister(site):
    """ Merengue admin unregistration callback """
    site.unregister(NewsCategory)
    site.unregister(NewsItem)
