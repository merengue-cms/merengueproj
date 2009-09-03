from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class SearchFormOptionsWidget(forms.Textarea):

    class Media:
        js = (
            '%sjs/search_form_options_widget.js' % settings.MEDIA_URL,
        )

    def __init__(self, attrs={}, search_form_selector_id='id_search_form'):
        self.search_form_selector_id=search_form_selector_id
        attrs.update({'class': 'SearchFormOptionsWidget'})
        super(SearchFormOptionsWidget, self).__init__(attrs)

    def render(self, *args, **kwargs):
        textarea = super(SearchFormOptionsWidget, self).render(*args, **kwargs)
        widget_text = u'%s' % textarea
        widget_text += u'<input type="hidden" name="search_form_selector_id" value="%s" />' % self.search_form_selector_id
        widget_text += u'<img src="%simg/ajax-loader-admin.gif" alt="%s" class="hide SearchFormOptionsWidgetLoading" />' % (settings.MEDIA_URL, _(u'Please wait...'))
        return mark_safe(widget_text)
