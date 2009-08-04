from django import template

register = template.Library()


@register.filter
def next_page_count(page):
    """Return the number of objects of the next page"""
    if page.has_next():
        next_page = page.paginator.page(page.number + 1)
        return len(next_page.object_list)
    return 0
