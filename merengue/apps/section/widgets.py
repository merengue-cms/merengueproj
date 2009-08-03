from django import forms
from django.conf import settings
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class ModifiedRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):

    def render(self, name, value, *args, **kwargs):
        rel_to = self.rel.to
        related_url = '%sadmin/%s/%s/' % (
                self.admin_site.basecontent.get_admin_absolute_url(),
                rel_to._meta.app_label,
                rel_to._meta.object_name.lower())
        self.widget.choices = self.choices
        output = [self.widget.render(name, value, *args, **kwargs)]
        # If the related object has an admin interface:
        if rel_to in self.admin_site._registry:
            # TODO: "id_" is hard-coded here. This should instead use
            # the correct API to determine the ID dynamically.
            output.append(u'<a href="%sadd/" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
                (related_url, name))
            output.append(u'<img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Add Another')))
        return mark_safe(u''.join(output))


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
