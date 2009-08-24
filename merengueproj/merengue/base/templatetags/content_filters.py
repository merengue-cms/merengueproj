from django.template import Library
from django.utils.translation import ugettext as _

register = Library()


@register.filter
def trans_yesno(value, arg=None):
    """
    Like django yesno built in filter, but with a translation call to all values
    """
    if arg is None:
        arg = _('yes,no,maybe')
    bits = arg.split(u',')
    if len(bits) < 2:
        return _(value) # Invalid arg.
    try:
        yes, no, maybe = bits
    except ValueError:
        # Unpack list of wrong size (no "maybe" value provided).
        yes, no, maybe = bits[0], bits[1], bits[1]
    if value is None:
        return _(maybe)
    if value:
        return _(yes)
    return _(no)
trans_yesno.is_safe = False


@register.filter
def basecontent_type(obj):
    """
    Returns meta class name
    """
    return obj._meta.verbose_name
