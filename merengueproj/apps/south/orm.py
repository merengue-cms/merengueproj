"""
South's fake ORM; lets you not have to write SQL inside migrations.
Roughly emulates the real Django ORM, to a point.
"""

import inspect

from django.db import models
from django.db.models.loading import cache

from south.db import db


class ModelsLocals(object):
    
    """
    Custom dictionary-like class to be locals();
    falls back to lowercase search for items that don't exist
    (because we store model names as lowercase).
    """
    
    def __init__(self, data):
        self.data = data
    
    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            return self.data[key.lower()]


class FakeORM(object):
    
    """
    Simulates the Django ORM at some point in time,
    using a frozen definition on the Migration class.
    """
    
    def __init__(self, cls, app):
        self.default_app = app
        self.cls = cls
        # Try loading the models off the migration class; default to no models.
        self.models = {}
        try:
            self.models_source = cls.models
        except AttributeError:
            return
        
        # Now, make each model's data into a FakeModel
        for name, data in self.models_source.items():
            # Make sure there's some kind of Meta
            if "Meta" not in data:
                data['Meta'] = {}
            try:
                app_name, model_name = name.split(".", 1)
            except ValueError:
                app_name = self.default_app
                model_name = name
                name = "%s.%s" % (app_name, model_name)
            
            self.models[name.lower()] = self.make_model(app_name, model_name, data)
        
        # And perform the second run to iron out any circular/backwards depends.
        self.retry_failed_fields()

    
    def __getattr__(self, key):
        fullname = (self.default_app+"."+key).lower()
        try:
            return self.models[fullname]
        except KeyError:
            raise AttributeError("The model '%s' from the app '%s' is not available in this migration." % (key, self.default_app))
    
    
    def __getitem__(self, key):
        key = key.lower()
        try:
            return self.models[key]
        except KeyError:
            try:
                app, model = key.split(".", 1)
            except ValueError:
                raise KeyError("The model '%s' is not in appname.modelname format." % key)
            else:
                raise KeyError("The model '%s' from the app '%s' is not available in this migration." % (model, app))
    
    
    def eval_in_context(self, code, app):
        "Evaluates the given code in the context of the migration file."
        
        # Drag in the migration module's locals (hopefully including models.py)
        fake_locals = dict(inspect.getmodule(self.cls).__dict__)
        
        # Remove all models from that (i.e. from modern models.py), to stop pollution
        for key, value in fake_locals.items():
            if isinstance(value, type) and issubclass(value, models.Model) and hasattr(value, "_meta"):
                del fake_locals[key]
        
        # We add our models into the locals for the eval
        fake_locals.update(dict([
            (name.split(".")[-1], model)
            for name, model in self.models.items()
        ]))
        
        # Make sure the ones for this app override.
        fake_locals.update(dict([
            (name.split(".")[-1], model)
            for name, model in self.models.items()
            if name.split(".")[0] == app
        ]))
        
        # Ourselves as orm, to allow non-fail cross-app referencing
        fake_locals['orm'] = self
        
        # And a fake _ function
        fake_locals['_'] = lambda x: x
        
        # Use ModelsLocals to make lookups work right for CapitalisedModels
        fake_locals = ModelsLocals(fake_locals)
        
        return eval(code, globals(), fake_locals)
    
    
    def make_meta(self, app, model, data, stub=False):
        "Makes a Meta class out of a dict of eval-able arguments."
        results = {}
        for key, code in data.items():
            # Some things we never want to use.
            if key in ["_bases"]:
                continue
            # Some things we don't want with stubs.
            if stub and key in ["order_with_respect_to"]:
                continue
            # OK, add it.
            try:
                results[key] = self.eval_in_context(code, app)
            except (NameError, AttributeError), e:
                raise ValueError("Cannot successfully create meta field '%s' for model '%s.%s': %s." % (
                    key, app, model, e
                ))
        return type("Meta", tuple(), results) 
    
    
    def make_model(self, app, name, data):
        "Makes a Model class out of the given app name, model name and pickled data."
        
        # Extract any bases out of Meta
        if "_bases" in data['Meta']:
            bases = data['Meta']['_bases']
        else:
            bases = ['django.db.models.Model']
        
        # Turn the Meta dict into a basic class
        meta = self.make_meta(app, name, data['Meta'], data.get("_stub", False))
        
        failed_fields = {}
        fields = {}
        stub = False
        
        # Now, make some fields!
        for fname, params in data.items():
            if fname == "_stub":
                stub = bool(params)
                continue
            elif fname == "Meta":
                continue
            elif not params:
                raise ValueError("Field '%s' on model '%s.%s' has no definition." % (fname, app, name))
            elif isinstance(params, (str, unicode)):
                # It's a premade definition string! Let's hope it works...
                code = params
            elif len(params) == 1:
                code = "%s()" % params[0]
            elif len(params) == 3:
                code = "%s(%s)" % (
                    params[0],
                    ", ".join(
                        params[1] +
                        ["%s=%s" % (n, v) for n, v in params[2].items()]
                    ),
                )
            else:
                raise ValueError("Field '%s' on model '%s.%s' has a weird definition length (should be 1 or 3 items)." % (fname, app, name))
            
            try:
                field = self.eval_in_context(code, app)
            except (NameError, AttributeError, AssertionError):
                # It might rely on other models being around. Add it to the
                # model for the second pass.
                failed_fields[fname] = code
            else:
                fields[fname] = field
        
        # Find the app in the Django core, and get its module
        more_kwds = {}
        app_module = models.get_app(app)
        more_kwds['__module__'] = app_module.__name__
        
        more_kwds['Meta'] = meta
        
        # Stop AppCache from changing!
        cache.app_models[app], old_app_models = {}, cache.app_models[app]
        
        # Make our model
        fields.update(more_kwds)
        
        model = type(
            name,
            tuple(map(ask_for_it_by_name, bases)),
            fields,
        )
        
        # Send AppCache back in time
        cache.app_models[app] = old_app_models
        
        # If this is a stub model, change Objects to a whiny class
        if stub:
            model.objects = WhinyManager()
            # Also, make sure they can't instantiate it
            model.__init__ = whiny_method
        else:
            model.objects = NoDryRunManager(model.objects)
        
        if failed_fields:
            model._failed_fields = failed_fields
        
        return model
    
    def retry_failed_fields(self):
        "Tries to re-evaluate the _failed_fields for each model."
        for modelkey, model in self.models.items():
            app, modelname = modelkey.split(".", 1)
            if hasattr(model, "_failed_fields"):
                for fname, code in model._failed_fields.items():
                    try:
                        field = self.eval_in_context(code, app)
                    except (NameError, AttributeError, AssertionError), e:
                        # It's failed again. Complain.
                        raise ValueError("Cannot successfully create field '%s' for model '%s': %s." % (
                            fname, modelname, e
                        ))
                    else:
                        # Startup that field.
                        model.add_to_class(fname, field)


class WhinyManager(object):
    "A fake manager that whines whenever you try to touch it. For stub models."
    
    def __getattr__(self, key):
        raise AttributeError("You cannot use items from a stub model.")


class NoDryRunManager(object):
    """
    A manager that always proxies through to the real manager,
    unless a dry run is in progress.
    """
    
    def __init__(self, real):
        self.real = real
    
    def __getattr__(self, name):
        if db.dry_run:
            raise AttributeError("You are in a dry run, and cannot access the ORM.\nWrap ORM sections in 'if not db.dry_run:', or if the whole migration is only a data migration, set no_dry_run = True on the Migration class.")
        return getattr(self.real, name)


def ask_for_it_by_name(name):
    "Returns an object referenced by absolute path."
    bits = name.split(".")
    modulename = ".".join(bits[:-1])
    module = __import__(modulename, {}, {}, bits[-1])
    return getattr(module, bits[-1])


def whiny_method(*a, **kw):
    raise ValueError("You cannot instantiate a stub model.")
