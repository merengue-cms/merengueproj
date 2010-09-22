# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
#
# This file is part of Merengue.
#
# Merengue is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Merengue is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Merengue.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

from django import template
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite as DjangoAdminSite
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models.base import ModelBase
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.functional import update_wrapper
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from merengue.base.adminforms import UploadConfigForm, BackupForm
from merengue.base.models import BaseContent
from merengue.utils import get_all_parents

OBJECT_ID_PREFIX = 'base_object_id_'
MODEL_ADMIN_PREFIX = 'base_model_admin_'


class BaseAdminSite(DjangoAdminSite):
    related_admin_sites = None
    base_model_admins = None

    def __init__(self, *args, **kwargs):
        self.apps_registered = []
        self.related_admin_sites = {}
        self.base_model_admins = {}
        self.base_object_ids = {}
        self.base_tools_model_admins = {}
        super(BaseAdminSite, self).__init__(*args, **kwargs)

    def admin_view(self, view, cacheable=False):

        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                return self.login(request)
            for key in kwargs.keys():
                if key.startswith(OBJECT_ID_PREFIX):
                    self.base_object_ids.update({key[len(OBJECT_ID_PREFIX):]: kwargs.pop(key)})
                if key.startswith(MODEL_ADMIN_PREFIX):
                    self.base_tools_model_admins.update({key[len(MODEL_ADMIN_PREFIX):]: kwargs.pop(key)})
            return view(request, *args, **kwargs)
        if not cacheable:
            inner = never_cache(inner)
        return update_wrapper(inner, view)

    def app_index(self, request, app_label, extra_context=None):
        user = request.user
        app_dict = {}
        for model, model_admin in self._registry.items():
            if app_label == model._meta.app_label:
                perms = {'add': True, 'change': True, 'delete': True}
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'admin_url': '%s/' % model.__name__.lower(),
                    'perms': perms,
                }
                if app_dict:
                    app_dict['models'].append(model_dict),
                else:
                    # First time around, now that we know there's
                    # something to display, add in the necessary meta
                    # information.
                    app_dict = {
                        'name': app_label.title(),
                        'app_url': '',
                        'has_module_perms': True,
                        'models': [model_dict],
                    }
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        app_dict['models'].sort(lambda x, y: cmp(x['name'], y['name']))
        context = {
            'title': _('%s administration') % capfirst(app_label),
            'app_list': [app_dict],
            'root_path': self.root_path,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.name)
        return render_to_response(self.app_index_template or ('admin/%s/app_index.html' % app_label,
            'admin/app_index.html'), context,
            context_instance=context_instance,
        )

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include
        from django.template.defaultfilters import slugify

        urlpatterns = super(BaseAdminSite, self).get_urls()
        related_urlpatterns = []

        # custom url definitions
        custom_patterns = patterns('',
            url(r'^control_panel/$',
                self.admin_view(self.control_panel),
                name='control_panel'),
            url(r'^admin_redirect/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
                self.admin_view(self.admin_redirect),
                name='admin_redirect'),
            url(r'^siteconfig/$',
                self.admin_view(self.site_configuration),
                name='site_configuration'),
            url(r'^siteconfig/save/$',
                self.admin_view(self.save_configuration),
                name='save_configuration'),
            url(r'^siteconfig/backup/$',
                self.admin_view(self.save_backup),
                name='save_backup'),
        )
        # related url definitions
        for model, model_admin in self._registry.iteritems():
            for key in self.related_admin_sites.keys():
                if issubclass(model, key):
                    for tool_name, related_admin_site in self.related_admin_sites[key].items():
                        related_admin_site.base_model_admins[model] = model_admin
                        related_urlpatterns += patterns('',
                            url(r'^%(app)s/%(model)s/(?P<%(pref)s%(tname)s>\d+)/%(tname)s/' % ({'app': model._meta.app_label,
                                                                                                'model': model._meta.module_name,
                                                                                                'pref': OBJECT_ID_PREFIX,
                                                                                                'tname': slugify(tool_name),
                                                                                               }),
                                include(related_admin_site.urls), {'%s%s' % (MODEL_ADMIN_PREFIX, slugify(tool_name)): model_admin}))

        return custom_patterns + related_urlpatterns + urlpatterns

    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Registers the given model(s) with the given admin class.

        It's copied from django one. The only difference is that this registration
        does not will raise AlreadyRegistered exception if you try register two times
        same model_or_iterable and admin_class. However, It will raise exception
        if you try to register same model_or_iterable with different admin_class.
        """
        if not admin_class:
            admin_class = ModelAdmin

        # Don't import the humongous validation code unless required
        if admin_class and settings.DEBUG:
            from django.contrib.admin.validation import validate
        else:
            validate = lambda model, adminclass: None

        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            # Here is the difference between django.contrib.admin.sites register and merengue one
            if model in self._registry and not isinstance(self._registry[model], admin_class):
                raise AlreadyRegistered('The model %s is already registered' % model.__name__)

            # If we got **options then dynamically construct a subclass of
            # admin_class with those **options.
            if options:
                # For reasons I don't quite understand, without a __module__
                # the created class appears to "live" in the wrong place,
                # which causes issues later on.
                options['__module__'] = __name__
                admin_class = type("%sAdmin" % model.__name__, (admin_class, ), options)

            # Validate (which might be a no-op)
            validate(admin_class, model)

            # Instantiate the admin class to save in the registry
            self._registry[model] = admin_class(model, self)

    def admin_redirect(self, request, content_type_id, object_id):
        """ redirect to content admin page or content related admin page in his section """
        try:
            content = ContentType.objects.get_for_id(content_type_id).get_object_for_this_type(id=object_id)
        except ObjectDoesNotExist:
            raise Http404
        admin_prefix = reverse('admin:index')
        model = content.__class__
        if isinstance(content, BaseContent):
            real_content = content.get_real_instance()
            if real_content is not None:
                content = real_content
                model = content.__class__
                related_sections = real_content.basesection_set.all()
                if related_sections.count() == 1:
                    # we have to redirect to the content related section
                    section = related_sections.get().real_instance
                    admin_prefix += 'section/section/%s/' % section.id
                    parents = get_all_parents(section.__class__)
                    section_sites = {}
                    [section_sites.update(self.related_admin_sites.get(parent, {})) for parent in parents]
                    section_sites.update(self.related_admin_sites[section.__class__])
                    #section_sites = self.related_admin_sites[section.__class__]
                    for admin_site in section_sites.values():
                        if model in admin_site._registry:
                            admin_prefix += admin_site.name + '/'
                            break
                elif getattr(self, 'get_plugin_site_prefix_for_model', False):
                    admin_prefix += self.get_plugin_site_prefix_for_model(model) + '/'
        return HttpResponseRedirect('%s%s/%s/%d/' % (admin_prefix, model._meta.app_label,
                                    model._meta.module_name, content.id))

    def site_configuration(self, request):
        from merengue.perms import utils as perms_api
        if not perms_api.can_manage_site(request.user):
            raise PermissionDenied
        from merengue.utils import restore_config
        if request.method == 'POST':
            if request.POST.get('_submit_configuration', None):
                form_configuration = UploadConfigForm(request.POST, request.FILES)
                if form_configuration.is_valid():
                    restore_config(form_configuration.cleaned_data['zipfile'])
                    request.user.message_set.create(message=_('Settings saved successfully'))
            elif request.POST.get('_submit_backup', None):
                form_backup = BackupForm(request.POST, request.FILES)
                if form_backup.is_valid():
                    form_backup.save()
                    request.user.message_set.create(message=_('Database created successfully'))
        form_configuration = UploadConfigForm()
        form_backup = BackupForm()
        return render_to_response('admin/siteconfig.html',
                                      {'form_configuration': form_configuration,
                                       'form_backup': form_backup,
                                      },
                                      context_instance=RequestContext(request))

    def save_configuration(self, request):
        from merengue.utils import save_config
        zip_name = datetime.now()
        response = HttpResponse(mimetype='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % zip_name.isoformat('-')
        buffer_zip = save_config()
        response.write(buffer_zip.getvalue())
        return response

    def save_backup(self, request):
        from cmsutils.db_utils import do_backupdb
        from merengue.utils import save_backupdb
        zip_name = 'backup_%s' % datetime.now().isoformat('-')
        response = HttpResponse(mimetype='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % zip_name
        path_backup = do_backupdb()
        buffer_zip = save_backupdb(path_backup)
        response.write(buffer_zip.getvalue())
        return response

    def index(self, request, extra_context=None):
        """ merengue admin index page. It's a friendly admin page """
        extra_context = extra_context or {}
        context = {
            'title': _('Site administration'),
            'root_path': self.root_path,
        }
        context.update(extra_context)
        context_instance = template.RequestContext(request, current_app=self.name)
        return render_to_response('admin/merengue_index.html', context,
            context_instance=context_instance,
        )

    def control_panel(self, request):
        """ admin control panel. Similar to django admin index page """
        return super(BaseAdminSite, self).index(request, {'title': _('Control Panel')})

    def _register_related(self, model_or_iterable, admin_class=None, related_to=None, **options):
        from merengue.base.admin import RelatedModelAdmin
        if not admin_class:
            raise Exception('Need a subclass of RelatedModelAdmin to register a related model admin' % admin_class.__name__)
        if not issubclass(admin_class, RelatedModelAdmin):
            raise Exception('%s modeladmin must be a subclass of RelatedModelAdmin' % admin_class.__name__)
        tool_name = admin_class and (getattr(admin_class, 'tool_name', None) or getattr(model_or_iterable._meta, 'module_name', None))
        if not tool_name:
            raise Exception('Can not register %s modeladmin without a tool_name' % admin_class.__name__)
        tool_label = getattr(admin_class, 'tool_label', None) or getattr(model_or_iterable._meta, 'verbose_name', None)

        if not related_to in self.related_admin_sites.keys():
            self.related_admin_sites[related_to] = {}
        if not tool_name in self.related_admin_sites[related_to].keys():
            self.related_admin_sites[related_to][tool_name] = RelatedAdminSite(
                name=tool_name,
                tool_label=tool_label)
        elif tool_name != self.related_admin_sites[related_to][tool_name].name:
            raise AlreadyRegistered('The related tool %s is already registered for model %s' %\
                                    (tool_name, related_to.__name__))
        related_admin_site = self.related_admin_sites[related_to][tool_name]
        related_admin_site.register(model_or_iterable, admin_class, **options)
        return related_admin_site

    def _get_admin_site_for_model(self, related_to, admin_sites_returned=None, branch=None):
        admin_sites_returned = admin_sites_returned or []
        branch = branch or []

        for model in self._registry.keys():
            if related_to == model or issubclass(model, related_to):
                admin_sites_returned.append(self)
                break

        for related_to_model, related_admin_site in self.related_admin_sites.items():
            for related_admin_site_tool_name, related_admin_site_value in related_admin_site.items():
                is_in_branch = False
                for model_branch in branch:
                    if model_branch == related_to or issubclass(related_to, model_branch) or issubclass(related_to, model_branch):
                        is_in_branch = True
                        break

                if not is_in_branch:
                    admin_sites_returned.extend(related_admin_site_value._get_admin_site_for_model(related_to, admin_sites_returned, branch + [related_to]))

        return admin_sites_returned


class RelatedModelRegistrable(object):

    steps = {}

    def set_steps(self, model_or_iterable, admin_class, related_to, **options):
        if related_to and not related_to in self.steps.keys():
            self.steps[related_to] = {}
            self.steps[related_to] = {}
        if model_or_iterable not in self.steps[related_to].keys():
            self.steps[related_to][model_or_iterable] = {}
        self.steps[related_to][model_or_iterable][admin_class] = options

    def register_related(self, model_or_iterable, admin_class=None, related_to=None, **options):
        self.set_steps(model_or_iterable, admin_class, related_to, **options)

        # Register model_or_iterable in every admin site which contains at related_to
        admin_sites = list(set(self._get_admin_site_for_model(related_to)))
        for admin_site in admin_sites:
            admin_site._register_related(model_or_iterable=model_or_iterable, admin_class=admin_class,
                                                related_to=related_to, **options)


        # Register the admin site related with model_or_iterable in every admin site of model_or_iterable
        admin_sites = list(set(self._get_admin_site_for_model(model_or_iterable)))
        for model_to, admin_site_attrs in self.steps.items():
            if not issubclass(model_or_iterable, model_to):
                continue
            for model, admin_models in admin_site_attrs.items():
                for admin_class, options in admin_models.items():
                    for admin_site in admin_sites:
                        admin_site._register_related(model_or_iterable=model, admin_class=admin_class,
                                                related_to=model_to, **options)


class AdminSite(BaseAdminSite, RelatedModelRegistrable):

    def __init__(self, *args, **kwargs):
        super(AdminSite, self).__init__(*args, **kwargs)
        self._plugin_sites = {}

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = super(AdminSite, self).get_urls()

        # custom url definitions
        for plugin_name, plugin_site in self._plugin_sites.items():
            urlpatterns += patterns('',
                url('^%s/' % plugin_name,
                    include(plugin_site.urls),
                ),
            )
        return urlpatterns

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        app_dict = {}
        user = request.user
        from merengue.perms import utils as perms_api
        manage_plugin_content = perms_api.can_manage_plugin_content(request.user)
        for plugin_name, site in self._plugin_sites.items():
            app_label = plugin_name

            if app_label in app_dict:
                continue

            if manage_plugin_content:
                name = app_label.split('.')[1:]
                app_dict[app_label] = {
                    'name': name and name[0].title() or '',
                    'app_url': app_label + '/',
                    'has_module_perms': manage_plugin_content,
                }

        # Sort the apps alphabetically.
        app_list = app_dict.values()
        app_list.sort(lambda x, y: cmp(x['name'], y['name']))

        extra_context.update(
            {'plugins': app_dict})
        return super(AdminSite, self).index(request, extra_context)

    def register_plugin_site(self, plugin_name):
        if plugin_name in self._plugin_sites.keys():
            return self._plugin_sites[plugin_name]
        plugin_site = PluginAdminSite(main_admin_site=self, plugin_name=plugin_name)
        self._plugin_sites[plugin_name]=plugin_site
        return plugin_site

    def unregister_plugin_site(self, plugin_name):
        if not plugin_name in self._plugin_sites.keys():
            return
        del(self._plugin_sites[plugin_name])

    def get_plugin_site(self, plugin_name):
        if plugin_name in self._plugin_sites.keys():
            return self._plugin_sites[plugin_name]
        return None

    def get_plugin_sites(self):
        return self._plugin_sites.values()

    def get_plugin_site_prefix_for_model(self, model):
        for plugin_name, plugin_site in self._plugin_sites.items():
            if model in plugin_site._registry:
                return plugin_name
        return None


class PluginAdminSite(BaseAdminSite, RelatedModelRegistrable):

    def __init__(self, *args, **kwargs):
        self.main_site = kwargs.pop('main_admin_site', None)
        self.i_am_plugin_site = True
        self.prefix = kwargs.pop('plugin_name', '')
        plugin_name = self.prefix.split('.')[1:]
        self.plugin_name = plugin_name and plugin_name[0] or ''
        super(PluginAdminSite, self).__init__(*args, **kwargs)
        self.related_admin_sites = self.main_site.related_admin_sites
        main_admin = reverse('admin:index')
        self.root_path = '%s%s/' % (main_admin, self.prefix)

    def index(self, request):
        return super(BaseAdminSite, self).index(request,
                                                {'title': _('%(plugin_name)s plugin administration') % {'plugin_name': self.plugin_name},
                                                 'inplugin': True,
                                                 'plugin_name': self.plugin_name})

    def app_index(self, request, app_label, extra_context=None):
        return super(PluginAdminSite, self).app_index(request, app_label, {'inplugin': True, 'plugin_name': self.plugin_name})


class RelatedAdminSite(BaseAdminSite):

    def __init__(self, name=None, app_name='admin', tool_label=None):
        super(RelatedAdminSite, self).__init__(name, app_name)
        self.tool_label = tool_label

    def register(self, model_or_iterable, admin_class=None, **options):
        super(RelatedAdminSite, self).register(model_or_iterable, admin_class, **options)
        model_admin = self._registry[model_or_iterable]
        if not model_admin.tool_name:
            # we set tool_name as admin site one, a good default value if tool_name was not defined in ModelAdmin class
            model_admin.tool_name = self.name

# This global object represents the default admin site, for the common case.
# You can instantiate AdminSite in your own code to create a custom admin site.
site = AdminSite()
