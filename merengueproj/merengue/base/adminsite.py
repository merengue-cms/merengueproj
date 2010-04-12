from django.conf import settings
from django import template
from django.db.models.base import ModelBase
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.admin.sites import AdminSite as DjangoAdminSite
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from merengue.base.models import BaseContent

OBJECT_ID_PREFIX = 'base_object_id_'
MODEL_ADMIN_PREFIX = 'base_model_admin_'
PLUGIN_ADMIN_PREFIX = 'plugin_admin'


class BaseAdminSite(DjangoAdminSite):
    related_admin_sites = None
    base_model_admins = None

    def __init__(self, *args, **kwargs):
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
                    section_sites = self.related_admin_sites[section.__class__]
                    for admin_site in section_sites.values():
                        if model in admin_site._registry:
                            admin_prefix += admin_site.name + '/'
                            break
        return HttpResponseRedirect('%s%s/%s/%d/' % (admin_prefix, model._meta.app_label,
                                    model._meta.module_name, content.id))

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
        self.plugin_site = PluginAdminSite(main_admin_site=self)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        urlpatterns = super(AdminSite, self).get_urls()

        # custom url definitions
        custom_patterns = patterns('',
            url('^' + PLUGIN_ADMIN_PREFIX + '/',
                include(self.plugin_site.urls),
            ),
        )
        return custom_patterns + urlpatterns

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        app_dict = {}
        user = request.user
        for model, model_admin in self.plugin_site._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

            if app_label in app_dict:
                continue

            if has_module_perms:
                app_dict[app_label] = {
                    'name': app_label.title(),
                    'app_url': PLUGIN_ADMIN_PREFIX + '/' + app_label + '/',
                    'has_module_perms': has_module_perms,
                }

        # Sort the apps alphabetically.
        app_list = app_dict.values()
        app_list.sort(lambda x, y: cmp(x['name'], y['name']))

        extra_context.update(
            {'plugins': app_dict})
        return super(AdminSite, self).index(request, extra_context)


class PluginAdminSite(BaseAdminSite, RelatedModelRegistrable):

    def __init__(self, *args, **kwargs):
        self.main_site = kwargs.pop('main_admin_site', None)
        self.i_am_plugin_site = True
        self.prefix = PLUGIN_ADMIN_PREFIX
        super(PluginAdminSite, self).__init__(*args, **kwargs)

    def index(self, request):
        return super(BaseAdminSite, self).index(request, {'title': _('Plugin administration'), 'inplugin': True})

    def app_index(self, request, app_label, extra_context=None):
        return super(PluginAdminSite, self).app_index(request, app_label, {'inplugin': True})


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
