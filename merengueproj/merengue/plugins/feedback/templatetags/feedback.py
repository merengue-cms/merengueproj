from django import template


register = template.Library()


@register.inclusion_tag('feedback/content_feedbacks_list.html', takes_context=True)
def content_feedbacks_list(context, content):
    return {'content': content}
