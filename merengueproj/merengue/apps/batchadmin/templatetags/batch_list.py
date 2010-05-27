from django.template import Library


register = Library()

def actions(context):
    """
    Track the number of times the action field has been rendered on the page,
    so we know which value to use.
    
    """
    context['batchadmin_index'] = context.get('batchadmin_index', -1) + 1
    return context
register.inclusion_tag("batchadmin/actions.html", takes_context=True)(actions)