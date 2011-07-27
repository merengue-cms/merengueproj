import transmeta

from django import forms
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from merengue.pluggable.utils import get_plugin
from merengue.section.models import BaseSection, Menu, ContentLink


class HotLinkForm(forms.ModelForm):

    def __init__(self, user, content, data=None, *args, **kwargs):
        super(HotLinkForm, self).__init__(data, *args, **kwargs)
        self.content = content
        self.only_menu = True
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
        try:
            get_plugin('standingout')
            self.fields['where_link'] = forms.ChoiceField(label=_('How do you want link?'),
                                                          choices=(('m', _('menu'),),
                                                                   ('s', _('standing out'),)))
            self.fields['visible_by_roles'].help_text = _('The roles that will see this menu. Only if you select the choice link like menu')
            self.only_menu = False
        except ImportError:
            pass

    class Meta:
        model = Menu
        exclude = ['parent', 'status', ] + \
                  transmeta.get_real_fieldname_in_each_language('help_text') + \
                  list(set(transmeta.get_real_fieldname_in_each_language('name')).difference(
                       set([transmeta.get_real_fieldname('name', settings.LANGUAGE_CODE)])))

    def is_menu(self, cleaned_data=None):
        cleaned_data = cleaned_data or getattr(self, 'cleaned_data', {})
        return self.only_menu or cleaned_data.get('where_link', None) == 'm'

    def is_standingout(self, cleaned_data=None):
        cleaned_data = cleaned_data or getattr(self, 'cleaned_data', {})
        return not self.only_menu and cleaned_data.get('where_link', None) == 's'

    def get_section(self, cleaned_data=None):
        cleaned_data = cleaned_data or getattr(self, 'cleaned_data', {})
        section = cleaned_data.get('section', None)
        if section:
            section = section.get_real_instance()
        return section

    def get_url_redirect(self, link):
        if isinstance(link, Menu):
            return link.url
        return self.get_section().get_absolute_url()

    def get_standingout_of_section(self, section):
        from plugins.standingout.models import StandingOut
        from plugins.standingout.utils import get_filter_ct
        return StandingOut.objects.filter(related_id=section.id).filter(
                                                 get_filter_ct(section))

    def clean(self):
        cleaned_data = super(HotLinkForm, self).clean()
        section = self.get_section(cleaned_data)
        if self.is_menu(cleaned_data) and section:
            main_menu = section.get_real_instance().main_menu
            menu = main_menu.get_children().filter(slug=cleaned_data['slug'])
            if menu:
                raise forms.ValidationError(_(u'Already exits a menu in your section with this slug'))
        if self.is_standingout(cleaned_data) and section:
            from plugins.standingout.utils import get_filter_ct
            standingouts = self.get_standingout_of_section(section).filter(
                                    obj_id=self.content.id).filter(
                                    get_filter_ct(self.content, 'obj'))
            if standingouts:
                raise forms.ValidationError(_(u'Already exits a standing out in your section with this content'))
        return cleaned_data

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', None)
        if not slug:
            name_lang = transmeta.get_real_fieldname('name', settings.LANGUAGE_CODE)
            slug = slugify(self.cleaned_data[name_lang])
        return slug

    def save(self, commit=False):
        section = section = self.get_section()
        if self.is_menu():
            menu = super(HotLinkForm, self).save(commit)
            menu_parent = section.main_menu
            menu.parent = menu_parent
            menu.save()
            ContentLink.objects.create(content=self.content, menu=menu)
            return menu
        elif self.is_standingout():
            standinouts = self.get_standingout_of_section(section)
            order = 0
            if standinouts:
                if standinouts[0].order:
                    order = standinouts[0].order + 1
                else:
                    order = standinouts.count() + 1
            from plugins.standingout.models import StandingOut
            stand = StandingOut.objects.create(obj=self.content,
                                               related=section,
                                               order=order)
            name_lang = transmeta.get_real_fieldname('name', settings.LANGUAGE_CODE)
            name_text = self.cleaned_data.get(name_lang)
            if name_text and name_text != self.content.name:
                title_lang = transmeta.get_real_fieldname('title', settings.LANGUAGE_CODE)
                setattr(stand, title_lang, name_text)
                stand.save()
            return stand
