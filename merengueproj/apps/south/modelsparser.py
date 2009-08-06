"""
Parsing module for models.py files. Extracts information in a more reliable
way than inspect + regexes.
"""

import re
import inspect
import parser
import symbol
import token
import keyword

from django.db import models


def name_that_thing(thing):
    "Turns a symbol/token int into its name."
    for name in dir(symbol):
        if getattr(symbol, name) == thing:
            return "symbol.%s" % name
    for name in dir(token):
        if getattr(token, name) == thing:
            return "token.%s" % name
    return str(thing)


def thing_that_name(name):
    "Turns a name of a symbol/token into its integer value."
    if name in dir(symbol):
        return getattr(symbol, name)
    if name in dir(token):
        return getattr(token, name)
    raise ValueError("Cannot convert '%s'" % name)


def prettyprint(tree, indent=0, omit_singles=False):
    "Prettyprints the tree, with symbol/token names. For debugging."
    if omit_singles and isinstance(tree, tuple) and len(tree) == 2:
        return prettyprint(tree[1], indent, omit_singles)
    if isinstance(tree, tuple):
        return " (\n%s\n" % "".join([prettyprint(x, indent+1) for x in tree]) + \
            (" " * indent) + ")"
    elif isinstance(tree, int):
        return (" " * indent) + name_that_thing(tree)
    else:
        return " " + repr(tree)


class STTree(object):
    
    "A syntax tree wrapper class."
    
    def __init__(self, tree):
        self.tree = tree
    
    
    def __eq__(self, other):
        return other.tree == self.tree
    
    
    def __hash__(self):
        return hash(self.tree)
    
    
    @property
    def root(self):
        return self.tree[0]
    
    
    @property
    def value(self):
        return self.tree
    
    
    def walk(self, recursive=True):
        """
        Yields (symbol, subtree) for the entire subtree.
        Comes out with node 1, node 1's children, node 2, etc.
        """
        stack = [self.tree]
        done_outer = False
        while stack:
            atree = stack.pop()
            if isinstance(atree, tuple):
                if done_outer:
                    yield atree[0], STTree(atree)
                if recursive or not done_outer:
                    for bit in reversed(atree[1:]):
                        stack.append(bit)
                    done_outer = True
    
    
    def flatten(self):
        "Yields the tokens/symbols in the tree only, in order."
        bits = []
        for sym, subtree in self.walk():
            if sym in token_map:
                bits.append(sym)
            elif sym == token.NAME:
                bits.append(subtree.value)
            elif sym == token.STRING:
                bits.append(subtree.value)
            elif sym == token.NUMBER:
                bits.append(subtree.value)
        return bits

    
    def reform(self):
        "Prints how the tree's input probably looked."
        return reform(self.flatten())
    
    
    def findAllType(self, ntype, recursive=True):
        "Returns all nodes with the given type in the tree."
        for symbol, subtree in self.walk(recursive=recursive):
            if symbol == ntype:
                yield subtree
    
    
    def find(self, selector):
        """
        Searches the syntax tree with a CSS-like selector syntax.
        You can use things like 'suite simple_stmt', 'suite, simple_stmt'
        or 'suite > simple_stmt'. Not guaranteed to return in order.
        """
        # Split up the overall parts
        patterns = [x.strip() for x in selector.split(",")]
        results = []
        for pattern in patterns:
            # Split up the parts
            parts = re.split(r'(?:[\s]|(>))+', pattern)
            # Take the first part, use it for results
            if parts[0] == "^":
                subresults = [self]
            else:
                subresults = list(self.findAllType(thing_that_name(parts[0])))
            recursive = True
            # For each remaining part, do something
            for part in parts[1:]:
                if not subresults:
                    break
                if part == ">":
                    recursive = False
                elif not part:
                    pass
                else:
                    thing = thing_that_name(part)
                    newresults = [
                        list(tree.findAllType(thing, recursive))
                        for tree in subresults
                    ]
                    subresults = []
                    for stuff in newresults:
                        subresults.extend(stuff)
                    recursive = True
            results.extend(subresults)
        return results
    
    
    def __str__(self):
        return prettyprint(self.tree)
    __repr__ = __str__
    

def get_model_tree(model):
    # Get the source of the model's file
    source = open(inspect.getsourcefile(model)).read().replace("\r\n", "\n").replace("\r","\n") + "\n"
    tree = STTree(parser.suite(source).totuple())
    # Now, we have to find it
    for poss in tree.find("compound_stmt"):
        if poss.value[1][0] == symbol.classdef and \
           poss.value[1][2][1].lower() == model.__name__.lower():
            # This is the tree
            return poss


token_map = {
    token.DOT: ".",
    token.LPAR: "(",
    token.RPAR: ")",
    token.EQUAL: "=",
    token.EQEQUAL: "==",
    token.COMMA: ",",
    token.LSQB: "[",
    token.RSQB: "]",
    token.AMPER: "&",
    token.BACKQUOTE: "`",
    token.CIRCUMFLEX: "^",
    token.CIRCUMFLEXEQUAL: "^=",
    token.COLON: ":",
    token.DOUBLESLASH: "//",
    token.DOUBLESLASHEQUAL: "//=",
    token.DOUBLESTAR: "**",
    token.DOUBLESLASHEQUAL: "**=",
    token.GREATER: ">",
    token.LESS: "<",
    token.GREATEREQUAL: ">=",
    token.LESSEQUAL: "<=",
    token.LBRACE: "{",
    token.RBRACE: "}",
    token.SEMI: ";",
    token.PLUS: "+",
    token.MINUS: "-",
    token.STAR: "*",
    token.SLASH: "/",
    token.VBAR: "|",
    token.PERCENT: "%",
    token.TILDE: "~",
    token.AT: "@",
    token.NOTEQUAL: "!=",
    token.LEFTSHIFT: "<<",
    token.RIGHTSHIFT: ">>",
    token.LEFTSHIFTEQUAL: "<<=",
    token.RIGHTSHIFTEQUAL: ">>=",
    token.PLUSEQUAL: "+=",
    token.MINEQUAL: "-=",
    token.STAREQUAL: "*=",
    token.SLASHEQUAL: "/=",
    token.VBAREQUAL: "|=",
    token.PERCENTEQUAL: "%=",
    token.AMPEREQUAL: "&=",
}


def reform(bits):
    "Returns the string that the list of tokens/symbols 'bits' represents"
    output = ""
    for bit in bits:
        if bit in token_map:
            output += token_map[bit]
        elif bit[0] in [token.NAME, token.STRING, token.NUMBER]:
            if keyword.iskeyword(bit[1]):
                output += " %s " % bit[1]
            else:
                if bit[1] not in symbol.sym_name:
                    output += bit[1]
    return output


def parse_arguments(argstr):
    """
    Takes a string representing arguments and returns the positional and 
    keyword argument list and dict respectively.
    All the entries in these are python source, except the dict keys.
    """
    # Get the tree
    tree = STTree(parser.suite(argstr).totuple())

    # Initialise the lists
    curr_kwd = None
    args = []
    kwds = {}
    
    # Walk through, assigning things
    testlists = tree.find("testlist")
    for i, testlist in enumerate(testlists):
        # BTW: A testlist is to the left or right of an =.
        items = list(testlist.walk(recursive=False))
        for j, item in enumerate(items):
            if item[0] == symbol.test:
                if curr_kwd:
                    kwds[curr_kwd] = item[1].reform()
                    curr_kwd = None
                elif j == len(items)-1 and i != len(testlists)-1:
                    # Last item in a group must be a keyword, unless it's last overall
                    curr_kwd = item[1].reform()
                else:
                    args.append(item[1].reform())
    return args, kwds


def extract_field(tree):
    # Collapses the tree and tries to parse it as a field def
    bits = tree.flatten()
    ## Check it looks right:
    # Second token should be equals
    if len(bits) < 2 or bits[1] != token.EQUAL:
        return
    ## Split into meaningful sections
    name = bits[0][1]
    declaration = bits[2:]
    # Find the first LPAR; stuff before that is the class.
    try:
        lpar_at = declaration.index(token.LPAR)
    except ValueError:
        return
    clsname = reform(declaration[:lpar_at])
    # Now, inside that, find the last RPAR, and we'll take the stuff between
    # them as the arguments
    declaration.reverse()
    rpar_at = (len(declaration) - 1) - declaration.index(token.RPAR)
    declaration.reverse()
    args = declaration[lpar_at+1:rpar_at]
    # Now, extract the arguments as a list and dict
    try:
        args, kwargs = parse_arguments(reform(args))
    except SyntaxError:
        return
    # OK, extract and reform it
    return name, clsname, args, kwargs
    


def get_model_fields(model, m2m=False):
    """
    Given a model class, will return the dict of name: field_constructor
    mappings.
    """
    tree = get_model_tree(model)
    if tree is None:
        raise ValueError("Cannot find source for model '%s'." % model)
    possible_field_defs = tree.find("^ > classdef > suite > stmt > simple_stmt > small_stmt > expr_stmt")
    field_defs = {}
    
    # Go through all the found defns, and try to parse them
    for pfd in possible_field_defs:
        field = extract_field(pfd)
        if field:
            field_defs[field[0]] = field[1:]

    inherited_fields = {}
    # Go through all bases (that are themselves models, but not Model)
    for base in model.__bases__:
        if base != models.Model and issubclass(base, models.Model):
            inherited_fields.update(get_model_fields(base))
    
    # Now, go through all the fields and try to get their definition
    source = model._meta.local_fields[:]
    if m2m:
        source += model._meta.local_many_to_many
    fields = {}
    for field in source:
        # Get its name
        fieldname = field.name
        if isinstance(field, models.related.RelatedObject):
            continue
        # Now, try to get the defn
        if fieldname in field_defs:
            fields[fieldname] = field_defs[fieldname]
        # Try the South definition workaround?
        elif hasattr(field, 'south_field_triple'):
            fields[fieldname] = field.south_field_triple()
        elif hasattr(field, 'south_field_definition'):
            print "Your custom field %s provides the outdated south_field_definition method.\nPlease consider implementing south_field_triple too; it's more reliably evaluated." % field
            fields[fieldname] = field.south_field_definition()
        # Try a parent?
        elif fieldname in inherited_fields:
            fields[fieldname] = inherited_fields[fieldname]
        # Is it a _ptr?
        elif fieldname.endswith("_ptr"):
            fields[fieldname] = ("models.OneToOneField", ["orm['%s.%s']" % (field.rel.to._meta.app_label, field.rel.to._meta.object_name)], {})
        # Try a default for 'id'.
        elif fieldname == "id":
            fields[fieldname] = ("models.AutoField", [], {"primary_key": "True"})
        else:
            fields[fieldname] = None
    
    return fields


def get_model_meta(model):
    """
    Given a model class, will return the dict representing the Meta class.
    """
    tree = get_model_tree(model)
    
    result = {}
    
    # First, try to get any unusual inherited classes
    for base in model.__bases__:
        if base is not models.Model:
            if hasattr(base, '_meta') and not base._meta.abstract:
                # Abstract models' fields are included anyway, and we don't
                # want extra dependencies
                if "_bases" not in result:
                    result['_bases'] = []
                result['_bases'].append(base.__module__ + "." + base.__name__)
    
    # Find all classes exactly two levels deep
    possible_meta_classes = set(tree.find("classdef classdef"))
    possible_meta_classes.difference(set(tree.find("classdef classdef classdef")))
    
    # Select only those called 'Meta', and expand all their assignments
    possible_meta_classes = [
        tree.find("^ > suite > stmt > simple_stmt > small_stmt > expr_stmt")
        for tree in possible_meta_classes
        if tree.value[2][1] == "Meta"
    ]
    
    if possible_meta_classes:
        # Now, for each possible definition, try it. (Only for last Meta,
        # since that's how python interprets it)
        for defn in possible_meta_classes[-1]:
            bits = defn.flatten()
            if len(bits) > 1 and bits[1] == token.EQUAL:
                result[bits[0][1]] = reform(bits[2:])
    
    return result or None
