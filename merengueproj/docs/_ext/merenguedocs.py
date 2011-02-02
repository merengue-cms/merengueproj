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
# 
# Taked from djangodocs.py file

"""
Sphinx plugins for Merengue documentation.
"""

from docutils import nodes, transforms

from sphinx import addnodes, roles
from sphinx.writers.html import SmartyPantsHTMLTranslator


def setup(app):
    app.add_crossref_type(
        directivename = "setting",
        rolename      = "setting",
        indextemplate = "pair: %s; setting",
    )
    app.add_crossref_type(
        directivename = "templatetag",
        rolename      = "ttag",
        indextemplate = "pair: %s; template tag"
    )
    app.add_crossref_type(
        directivename = "templatefilter",
        rolename      = "tfilter",
        indextemplate = "pair: %s; template filter"
    )
    app.add_crossref_type(
        directivename = "fieldlookup",
        rolename      = "lookup",
        indextemplate = "pair: %s, field lookup type",
    )
    app.add_description_unit(
        directivename = "django-admin",
        rolename      = "djadmin",
        indextemplate = "pair: %s; django-admin command",
        parse_node    = parse_django_admin_node,
    )
    app.add_description_unit(
        directivename = "django-admin-option",
        rolename      = "djadminopt",
        indextemplate = "pair: %s; django-admin command-line option",
        parse_node    = parse_django_adminopt_node,
    )
    app.add_config_value('merengue_next_version', '0.0', True)
    app.add_directive('versionadded', parse_version_directive, 1, (1, 1, 1))
    app.add_directive('versionchanged', parse_version_directive, 1, (1, 1, 1))
    app.add_transform(SuppressBlockquotes)


def parse_version_directive(name, arguments, options, content, lineno,
                      content_offset, block_text, state, state_machine):
    env = state.document.settings.env
    is_nextversion = env.config.merengue_next_version == arguments[0]
    ret = []
    node = addnodes.versionmodified()
    ret.append(node)
    if not is_nextversion:
        if len(arguments) == 1:
            linktext = 'Please, see the release notes <releases-%s>' % (arguments[0])
            xrefs = roles.xfileref_role('ref', linktext, linktext, lineno, state)
            node.extend(xrefs[0])
        node['version'] = arguments[0]
    else:
        node['version'] = "Development version"
    node['type'] = name
    if len(arguments) == 2:
        inodes, messages = state.inline_text(arguments[1], lineno+1)
        node.extend(inodes)
        if content:
            state.nested_parse(content, content_offset, node)
        ret = ret + messages
    env.note_versionchange(node['type'], node['version'], node, lineno)
    return ret


class SuppressBlockquotes(transforms.Transform):
    """
    Remove the default blockquotes that encase indented list, tables, etc.
    """
    default_priority = 300
    
    suppress_blockquote_child_nodes = (
        nodes.bullet_list, 
        nodes.enumerated_list, 
        nodes.definition_list,
        nodes.literal_block, 
        nodes.doctest_block, 
        nodes.line_block, 
        nodes.table
    )

    def apply(self):
        for node in self.document.traverse(nodes.block_quote):
            if len(node.children) == 1 and isinstance(node.children[0], self.suppress_blockquote_child_nodes):
                node.replace_self(node.children[0])

class DjangoHTMLTranslator(SmartyPantsHTMLTranslator):
    """
    Django-specific reST to HTML tweaks.
    """

    # Don't use border=1, which docutils does by default.
    def visit_table(self, node):
        self.body.append(self.starttag(node, 'table', CLASS='docutils'))

    # <big>? Really?
    def visit_desc_parameterlist(self, node):
        self.body.append('(')
        self.first_param = 1

    def depart_desc_parameterlist(self, node):
        self.body.append(')')
        pass

    #
    # Don't apply smartypants to literal blocks
    #
    def visit_literal_block(self, node):
        self.no_smarty += 1
        SmartyPantsHTMLTranslator.visit_literal_block(self, node)

    def depart_literal_block(self, node):
        SmartyPantsHTMLTranslator.depart_literal_block(self, node)
        self.no_smarty -= 1

    #
    # Turn the "new in version" stuff (versionadded/versionchanged) into a
    # better callout -- the Sphinx default is just a little span,
    # which is a bit less obvious that I'd like.
    #
    # FIXME: these messages are all hardcoded in English. We need to chanage 
    # that to accomodate other language docs, but I can't work out how to make
    # that work.
    #
    version_text = {
        'deprecated':       'Deprecated in Merengue %s',
        'versionchanged':   'Changed in Merengue %s',
        'versionadded':     'New in Merengue %s',
    }

    def visit_versionmodified(self, node):
        self.body.append(
            self.starttag(node, 'div', CLASS=node['type'])
        )
        title = "%s%s" % (
            self.version_text[node['type']] % node['version'],
            len(node) and ":" or "."
        )
        self.body.append('<span class="title">%s</span> ' % title)

    def depart_versionmodified(self, node):
        self.body.append("</div>\n")

    def visit_section(self, node):
        old_ids = node.get('ids', [])
        node['ids'] = ['s-' + i for i in old_ids]
        node['ids'].extend(old_ids)
        SmartyPantsHTMLTranslator.visit_section(self, node)
        node['ids'] = old_ids

def parse_django_admin_node(env, sig, signode):
    command = sig.split(' ')[0]
    env._django_curr_admin_command = command
    title = "django-admin.py %s" % sig
    signode += addnodes.desc_name(title, title)
    return sig

def parse_django_adminopt_node(env, sig, signode):
    """A copy of sphinx.directives.CmdoptionDesc.parse_signature()"""
    from sphinx import addnodes
    from sphinx.domains.std import option_desc_re
    count = 0
    firstname = ''
    for m in option_desc_re.finditer(sig):
        optname, args = m.groups()
        if count:
            signode += addnodes.desc_addname(', ', ', ')
        signode += addnodes.desc_name(optname, optname)
        signode += addnodes.desc_addname(args, args)
        if not count:
            firstname = optname
        count += 1
    if not firstname:
        raise ValueError
    return firstname

