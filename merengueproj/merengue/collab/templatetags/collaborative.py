from django import template

register = template.Library()


def collaborative_comments(context, content):
    return {}
register.inclusion_tag("collab/collaborative_comments.html", takes_context=True)(collaborative_comments)


def collaborative_translation(context, content):
    return {}
register.inclusion_tag("collab/collaborative_translation.html", takes_context=True)(collaborative_translation)
