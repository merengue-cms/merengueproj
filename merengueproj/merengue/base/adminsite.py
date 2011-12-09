# Copyright (c) 2010 by Yaco Sistemas
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
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models.base import ModelBase
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.functional import update_wrapper
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from merengue.base.adminforms import UploadConfigForm
from merengue.base.models import BaseContent
from merengue.perms import utils as perms_api
from merengue.base.actions import delete_selected

OBJECT_ID_PREFIX = 'base_object_id_'
MODEL_ADMIN_PREFIX = 'base_model_admin_'


class BaseAdminSite(DjangoAdminSite):
    base_model_admins = None
    index_template = 'admin/django_index.html'  # Django legacy index template

    def __init__(self, *args, **kwargs):
        self._models_registry = {}
        self.apps_registered = []
        self.base_model_admins = {}
        self.base_object_ids = {}
        self.base_tools_model_admins = {}
        self.related_registry = {}
        self.tools = {}
        super(BaseAdminSite, self).__init__(*args, **kwargs)
        if hasattr(self, '_actions') and self._actions.get('delete_selected', None):
            self._actions['delete_selected'] = delete_selected

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
        from django.conf.urls.defaults import patterns, url

        urlpatterns = super(BaseAdminSite, self).get_urls()
        #related_urlpatterns = []

        # custom url definitions
        custom_patterns = patterns('',
            url(r'^django_admin/$',
                self.admin_view(self.django_admin),
                name='django_admin'),
            url(r'^admin_redirect/(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<extra_url>.*)$',
                self.admin_view(self.admin_redirect),
                name='admin_redirect'),
            url(r'^models/$',
                self.admin_view(self.models_index),
                name='models_index'),
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
        return custom_patterns + urlpatterns

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
            validate = lambda model, adminclass: None  # pyflakes:ignore

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

    def register_model(self, model_or_iterable, admin_class=None, **options):
        """ Is a special register function which register a managed model.
            This makes Merengue know the list of managed contents """
        self.register(model_or_iterable, admin_class, **options)
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            self._models_registry[model] = self._registry[model]

    def unregister_model(self, model_or_iterable):
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model in self._models_registry.keys():
                del(self._models_registry[model])
            if model in self._registry.keys():
                del(self._registry[model])

    def admin_redirect(self, request, content_type_id, object_id, extra_url=''):
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
                related_sections = real_content.sections.all()
                if related_sections.count() == 1:
                    # we have to redirect to the content related section
                    section = related_sections.get().get_real_instance()
                    tool = self.get_tool_for_model(section.__class__, real_content.__class__)
                    if tool:
                        admin_prefix += '%s%s/' % (self.get_prefix_for_model(section.__class__), section.id)
                        admin_prefix += '%s/' % tool[0].tool_name
                    else:
                        admin_prefix += self.get_prefix_for_model(model)
                else:
                    admin_prefix += self.get_prefix_for_model(model)
        else:
            admin_prefix += self.get_prefix_for_model(model)
        return HttpResponseRedirect('%s%d/%s' % (admin_prefix, content.id, extra_url))

    def get_tool_for_model(self, model, managed_model):
        for klass in model.mro():
            tool = self.related_registry.get(klass, {}).get(managed_model, None)
            if tool:
                return tool
        return None

    def get_prefix_for_model(self, model):
        admin_prefix = ''
        if getattr(self, 'get_plugin_site_prefix_for_model', False):
            plugin_prefix = self.get_plugin_site_prefix_for_model(model)
            if plugin_prefix:
                admin_prefix += self.get_plugin_site_prefix_for_model(model) + '/'
        admin_prefix += '%s/%s/' % (model._meta.app_label, model._meta.module_name)
        return admin_prefix

    def models_index(self, request, extra_context=None):
        """ Index with all managed content types admin view """
        model_list = []
        for model, model_admin in self._models_registry.items():
            model_dict = {
                'name': capfirst(model._meta.verbose_name_plural),
                'admin_url': reverse('admin:%s_%s_changelist' % (model._meta.app_label, model._meta.module_name)),
                'model': model,
            }
            model_list.append(model_dict)
            # Sort the models alphabetically
            model_list.sort(key=lambda x: x['name'])
        context = {
            'title': _('Content types'),
            'model_list': model_list,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.name)
        return render_to_response(
            'admin/model_index.html', context,
            context_instance=context_instance,
        )

    def site_configuration(self, request):
        perms_api.assert_manage_site(request.user)
        from merengue.utils import restore_config
        form_configuration = UploadConfigForm()
        if request.method == 'POST':
            if request.POST.get('_submit_configuration', None):
                form_configuration = UploadConfigForm(request.POST, request.FILES)
                if form_configuration.is_valid():
                    restore_config(form_configuration.cleaned_data['zipfile'])
                    request.user.message_set.create(message=_('Settings saved successfully'))
                    form_configuration = UploadConfigForm()
        return render_to_response('admin/siteconfig.html',
                                      {'form_configuration': form_configuration},
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

    def django_admin(self, request):
        """ admin control panel. Similar to django admin index page """
        return super(BaseAdminSite, self).index(request, {'title': _('Django admin')})


class RelatedModelRegistrable(object):

    def register_related(self, model_or_iterable, admin_class=None, related_to=None, **options):

        if not model_or_iterable or not admin_class or not related_to:
            return
        tool_name = admin_class and (getattr(admin_class, 'tool_name', None) or getattr(model_or_iterable._meta, 'module_name', None))
        if not tool_name:
            raise Exception('Can not register %s modeladmin without a tool_name' % admin_class.__name__)

        model_tools = self.tools.get(related_to, {})

        if tool_name in model_tools and admin_class != model_tools[tool_name].__class__:
            raise AlreadyRegistered('Already registered a modeladmin with %s as tool_name' % tool_name)

        model_admin = model_tools.get(tool_name, admin_class(model_or_iterable, self))
        model_tools[tool_name] = model_admin
        base_model_registry = self.related_registry.get(related_to, {})
        related_modeladmins = base_model_registry.get(model_or_iterable, [])
        if model_admin not in related_modeladmins:
            related_modeladmins += [model_admin]
        base_model_registry[model_or_iterable] = related_modeladmins
        self.related_registry[related_to] = base_model_registry
        self.tools[related_to] = model_tools

    def unregister_related(self, model_or_iterable, admin_class=None, related_to=None, **options):

        if not model_or_iterable or not admin_class or not related_to:
            return
        tool_name = admin_class and (getattr(admin_class, 'tool_name', None) or getattr(model_or_iterable._meta, 'module_name', None))
        if not tool_name:
            raise Exception('Can not unregister %s modeladmin without a tool_name' % admin_class.__name__)

        model_tools = self.tools.get(related_to, {})
        if tool_name in model_tools and admin_class != model_tools[tool_name].__class__:
            raise AlreadyRegistered('Already registered a modeladmin with %s as tool_name' % tool_name)

        model_admin = model_tools.get(tool_name, admin_class(model_or_iterable, self))
        del model_tools[tool_name]
        base_model_registry = self.related_registry.get(related_to, {})
        related_modeladmins = base_model_registry.get(model_or_iterable, [])
        if model_admin not in related_modeladmins:
            related_modeladmins += [model_admin]
        del base_model_registry[model_or_iterable]
        self.related_registry[related_to] = base_model_registry
        self.tools[related_to] = model_tools


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
        from merengue.pluggable.utils import get_plugin_config

        extra_context = extra_context or {}
        app_dict = {}
        manage_plugin_content = perms_api.can_manage_plugin_content(request.user)
        for plugin_name, site in self._plugin_sites.items():
            app_label = plugin_name

            if app_label in app_dict:
                continue

            if manage_plugin_content:
                name = app_label.split('.')[1:]
                name = name and name[0] or ''
                config = get_plugin_config(name)
                app_dict[app_label] = {
                    'name': name.title(),
                    'app_url': app_label + '/',
                    'has_module_perms': manage_plugin_content,
                    'description': getattr(config, 'description', None),
                    'version': getattr(config, 'version', None),
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
        self._plugin_sites[plugin_name] = plugin_site
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
    index_template = 'admin/index.html'  # Plugin aware index template

    def __init__(self, *args, **kwargs):
        self.main_site = kwargs.pop('main_admin_site', None)
        self.i_am_plugin_site = True
        self.prefix = kwargs.pop('plugin_name', '')
        plugin_name = self.prefix.split('.')[1:]
        self.plugin_name = plugin_name and plugin_name[0] or ''
        super(PluginAdminSite, self).__init__(*args, **kwargs)
        main_admin = reverse('admin:index')
        self.related_registry = self.main_site.related_registry
        self.tools = self.main_site.tools
        self.root_path = '%s%s/' % (main_admin, self.prefix)

    def index(self, request):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.

        Code taken of django.contrib.admin.sites module. We have change the
        permissions to see all models admins.
        """
        extra_context = {
            'title': _('%(plugin_name)s plugin administration') % {'plugin_name': self.plugin_name},
            'inplugin': True,
            'plugin_name': self.plugin_name,
        }
        app_dict = {}
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            # in plugin site admin
            has_module_perms = perms_api.can_manage_plugin_content(request.user)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'admin_url': mark_safe('%s/%s/' % (app_label, model.__name__.lower())),
                        'perms': perms,
                    }
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'app_url': app_label + '/',
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = app_dict.values()
        app_list.sort(lambda x, y: cmp(x['name'], y['name']))

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(lambda x, y: cmp(x['name'], y['name']))

        context = {
            'title': _('Site administration'),
            'app_list': app_list,
            'root_path': self.root_path,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.name)
        return render_to_response(
            self.index_template or 'admin/index.html', context,
            context_instance=context_instance,
        )
    index = never_cache(index)

    def app_index(self, request, app_label, extra_context=None):
        return super(PluginAdminSite, self).app_index(request, app_label, {'inplugin': True, 'plugin_name': self.plugin_name})


# This global object represents the default admin site, for the common case.
# You can instantiate AdminSite in your own code to create a custom admin site.
site = AdminSite()
