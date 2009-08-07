"""
Like south.modelsparser, but using introspection where possible
rather than direct inspection of models.py.
"""

import datetime

import modelsparser
from south.utils import get_attribute

from django.db import models
from django.contrib.localflavor import us
from django.db.models.base import ModelBase
from django.db.models.fields import NOT_PROVIDED
from django.conf import settings
from django.utils.functional import Promise
from django.contrib.contenttypes import generic
from django.utils.datastructures import SortedDict

NOISY = True

# Gives information about how to introspect certain fields.
# This is a list of triples; the first item is a list of fields it applies to,
# (note that isinstance is used, so superclasses are perfectly valid here)
# the second is a list of positional argument descriptors, and the third
# is a list of keyword argument descriptors.
# Descriptors are of the form:
#  [attrname, options]
# Where attrname is the attribute on the field to get the value from, and options
# is an optional dict.
#
# The introspector uses the combination of all matching entries, in order.
introspection_details = [
    (
        (models.Field, ),
        [],
        {
            "null": ["null", {"default": False}],
            "blank": ["blank", {"default": False, "ignore_if":"primary_key"}],
            "primary_key": ["primary_key", {"default": False}],
            "max_length": ["max_length", {"default": None}],
            "unique": ["_unique", {"default": False}],
            "db_index": ["db_index", {"default": False}],
            "default": ["default", {"default": NOT_PROVIDED}],
            "db_column": ["db_column", {"default": None}],
            "db_tablespace": ["db_tablespace", {"default": settings.DEFAULT_INDEX_TABLESPACE}],
        },
    ),
    (
        (models.ForeignKey, models.OneToOneField),
        [],
        {
            "to": ["rel.to", {}],
            "to_field": ["rel.field_name", {"default_attr": "rel.to._meta.pk.name"}],
            "related_name": ["rel.related_name", {"default": None}],
            "db_index": ["db_index", {"default": True}],
        },
    ),
    (
        (models.ManyToManyField,),
        [],
        {
            "to": ["rel.to", {}],
            "symmetrical": ["rel.symmetrical", {"default": True}],
        },
    ),
    (
        (models.DateField, models.TimeField),
        [],
        {
            "auto_now": ["auto_now", {"default": False}],
            "auto_now_add": ["auto_now_add", {"default": False}],
        },
    ),
    (
        (models.DecimalField, ),
        [],
        {
            "max_digits": ["max_digits", {"default": None}],
            "decimal_places": ["decimal_places", {"default": None}],
        },
    ),
    (
        (models.BooleanField, ),
        [],
        {
            "default": ["default", {"default": NOT_PROVIDED, "converter": bool}],
        },
    ),
    (
        (models.FilePathField, ),
        [],
        {
            "path": ["path", {"default": ''}],
            "match": ["match", {"default": None}],
            "recursive": ["recursive", {"default": False}],
        },
    ),
    (
        (generic.GenericRelation, ),
        [],
        {
            "to": ["rel.to", {}],
            "symmetrical": ["rel.symmetrical", {"default": True}],
            "object_id_field": ["object_id_field_name", {"default": "object_id"}],
            "content_type_field": ["content_type_field_name", {"default": "content_type"}],
            "blank": ["blank", {"default": True}],
        },
    ),
]

# Similar, but for Meta, so just the inner level (kwds).
meta_details = {
    "db_table": ["db_table", {"default_attr_concat": ["%s_%s", "app_label", "module_name"]}],
    "db_tablespace": ["db_tablespace", {"default": settings.DEFAULT_TABLESPACE}],
    "unique_together": ["unique_together", {"default": []}],
}

# 2.4 compatability
any = lambda x: reduce(lambda y, z: y or z, x, False)


def can_introspect(field):
    """
    Returns True if we are allowed to introspect this field, False otherwise.
    ('allowed' means 'in core'. Custom fields can declare they are introspectable
    by the default South rules by adding the attribute _south_introspects = True.)
    """
    # Check for special attribute
    if hasattr(field, "_south_introspects") and field._south_introspects:
        return True
    # Check it's a core field (one I've written for)
    module = field.__class__.__module__
    return module.startswith("django.db") or module.startswith("django.contrib.gis") or module.startswith("django.contrib.localflavor") or module.startswith("django.contrib.contenttypes.generic")


def matching_details(field):
    """
    Returns the union of all matching entries in introspection_details for the field.
    """
    our_args = []
    our_kwargs = {}
    for classes, args, kwargs in introspection_details:
        if any([isinstance(field, x) for x in classes]):
            our_args.extend(args)
            our_kwargs.update(kwargs)
    return our_args, our_kwargs


class IsDefault(Exception):
    """
    Exception for when a field contains its default value.
    """


def get_value(field, descriptor):
    """
    Gets an attribute value from a Field instance and formats it.
    """
    attrname, options = descriptor
    value = get_attribute(field, attrname)
    # Lazy-eval functions get eval'd.
    # Annoyingly, we can't do an isinstance() test
    if isinstance(value, Promise):
        value = unicode(value)
    # If the value is the same as the default, omit it for clarity
    if "default" in options and value == options['default']:
        raise IsDefault
    # If there's an ignore_if, use it
    if "ignore_if" in options:
        if get_attribute(field, options['ignore_if']):
            raise IsDefault
    # Some default values need to be gotten from an attribute too.
    if "default_attr" in options:
        default_value = get_attribute(field, options['default_attr'])
        if value == default_value:
            raise IsDefault
    # Some are made from a formatting string and several attrs (e.g. db_table)
    if "default_attr_concat" in options:
        format, attrs = options['default_attr_concat'][0], options['default_attr_concat'][1:]
        default_value = format % tuple(map(lambda x: get_attribute(field, x), attrs))
        if value == default_value:
            raise IsDefault
    # Models get their own special repr()
    if isinstance(value, ModelBase):
        # If it's a proxy model, follow it back to its non-proxy parent
        if getattr(value._meta, "proxy", False):
            value = value._meta.proxy_for_model
        return "orm['%s.%s']" % (value._meta.app_label, value._meta.object_name)
    # Callables get called.
    elif callable(value):
        # Datetime.datetime.now is special, as we can access it from the eval
        # context (and because it changes all the time; people will file bugs otherwise).
        if value == datetime.datetime.now:
            return "datetime.datetime.now"
        if value == datetime.date.today:
            return "datetime.date.today"
        # All other callables get called.
        value = value()
    # Now, apply the converter func if there is one
    if "converter" in options:
        value = options['converter'](value)
    # Return the final value
    return repr(value)


def introspector(field):
    """
    Given a field, introspects its definition triple.
    """
    arg_defs, kwarg_defs = matching_details(field)
    args = []
    kwargs = {}
    # For each argument, use the descriptor to get the real value.
    for defn in arg_defs:
        try:
            args.append(get_value(field, defn))
        except IsDefault:
            pass
    for kwd, defn in kwarg_defs.items():
        try:
            kwargs[kwd] = get_value(field, defn)
        except IsDefault:
            pass
    return args, kwargs


def get_model_fields(model, m2m=False):
    """
    Given a model class, returns a dict of {field_name: field_triple} defs.
    """
    
    field_defs = SortedDict()
    inherited_fields = {}
    
    # Go through all bases (that are themselves models, but not Model)
    for base in model.__bases__:
        if base != models.Model and issubclass(base, models.Model):
            # Looks like we need their fields, Ma.
            inherited_fields.update(get_model_fields(base))
    
    # Now, ask the parser to have a look at this model too.
    try:
        parser_fields = modelsparser.get_model_fields(model, m2m) or {}
    except TypeError: # Almost certainly a not-real module
        parser_fields = {}
    
    # Now, go through all the fields and try to get their definition
    source = model._meta.local_fields[:]
    if m2m:
        source += model._meta.local_many_to_many
    
    for field in source:
        # Does it define a south_field_triple method?
        if hasattr(field, "south_field_triple"):
            if NOISY:
                print " ( Nativing field: %s" % field.name
            field_defs[field.name] = field.south_field_triple()
        # Can we introspect it?
        elif can_introspect(field):
            #if NOISY:
            #    print "Introspecting field: %s" % field.name
            # Get the full field class path.
            field_class = field.__class__.__module__ + "." + field.__class__.__name__
            # Run this field through the introspector
            args, kwargs = introspector(field)
            # That's our definition!
            field_defs[field.name] = (field_class, args, kwargs)
        # Hmph. Is it parseable?
        elif parser_fields.get(field.name, None):
            if NOISY:
                print " ( Parsing field: %s" % field.name
            field_defs[field.name] = parser_fields[field.name]
        # Shucks, no definition!
        else:
            if NOISY:
                print " ( Nodefing field: %s" % field.name
            field_defs[field.name] = None
    
    return field_defs


def get_model_meta(model):
    """
    Given a model class, will return the dict representing the Meta class.
    """
    
    # Get the introspected attributes
    meta_def = {}
    for kwd, defn in meta_details.items():
        try:
            meta_def[kwd] = get_value(model._meta, defn)
        except IsDefault:
            pass
    
    return meta_def
