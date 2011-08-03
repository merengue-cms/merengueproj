import transmeta

from django import forms
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from merengue.section.models import BaseSection, Menu, ContentLink


class HotLinkForm(forms.ModelForm):

    def __init__(self, user, content, data=None, *args, **kwargs):
        super(HotLinkForm, self).__init__(data, *args, **kwargs)
        self.content = content
        if user.is_superuser:
            choices = BaseSection.objects.all()
        else:
            class_names = ['basesection']
            subclasses = BaseSection.get_subclasses()
            class_names += [subclass.__name__.lower() for subclass in subclasses]
            choices = user.contents_owned.filter(class_name__in=class_names)
        if choices.count() == 1:
            self.fields['section'] = forms.ModelChoiceField(initial=choices[0],
                                                             queryset=choices,
                                                             label='',
                                                             widget=forms.HiddenInput)
        else:
            self.fields['section'] = forms.ModelChoiceField(queryset=choices,
                                                             label=_('Section'),
                                                             required=True,
                                                             help_text=_('Choose a section where save the menu'))
        name_lang = transmeta.get_real_fieldname('name', settings.LANGUAGE_CODE)
        self.fields['slug'].required = False
        if not data:
            self.fields['slug'].label = ''
            self.fields['slug'].widget = forms.HiddenInput()
        self.fields[name_lang].label = _('Name')
        self.fields[name_lang].initial = getattr(content, name_lang, unicode(content))

    class Meta:
        model = Menu
        exclude = ['parent', 'status', ] + \
                  transmeta.get_real_fieldname_in_each_language('help_text') + \
                  list(set(transmeta.get_real_fieldname_in_each_language('name')).difference(
                       set([transmeta.get_real_fieldname('name', settings.LANGUAGE_CODE)])))

    def clean(self):
        cleaned_data = super(HotLinkForm, self).clean()
        section = cleaned_data.get('section', None)
        if section:
            main_menu = section.get_real_instance().main_menu
            menu = main_menu.get_children().filter(slug=cleaned_data['slug'])
            if menu:
                raise forms.ValidationError(_(u'Already exits a menu in your section with this slug'))
        return cleaned_data

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', None)
        if not slug:
            name_lang = transmeta.get_real_fieldname('name', settings.LANGUAGE_CODE)
            slug = slugify(self.cleaned_data[name_lang])
        return slug

    def save(self, commit=False):
        menu = super(HotLinkForm, self).save(commit)
        section = self.cleaned_data['section'].get_real_instance()
        menu_parent = section.main_menu
        menu.parent = menu_parent
        menu.save()
        ContentLink.objects.create(content=self.content, menu=menu)
        return menu
