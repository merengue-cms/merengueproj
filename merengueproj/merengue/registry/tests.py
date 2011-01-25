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

"""
Tests for merengue.registry application
"""

__test__ = {"doctest": """
>>> from merengue.registry import register
>>> from merengue.registry.items import RegistrableItem
>>> from merengue.registry import params

>>> config_params = [
...    params.Bool(name='is_human', default=True),
...    params.Integer(name='age'),
...    params.List(name='friends', choices=('Juan', 'Luis', 'Pepe'))
... ]
>>> config_params
[<True, Bool>, <<class 'merengue.registry.params.NOT_PROVIDED'>, Integer>, <<class 'merengue.registry.params.NOT_PROVIDED'>, List>]
>>> config = params.ConfigDict(config_params, {'age': 25, 'friends': ('Juan', )})
>>> config
{'is_human': <True, Bool>, 'age': <25, Integer>, 'friends': <('Juan',), List>}
>>> config.update(params.ConfigDict(config_params, {'age': 40}))
>>> config
{'is_human': <True, Bool>, 'age': <40, Integer>, 'friends': <('Juan',), List>}

>>> class PersonItem(RegistrableItem):
...     config_params = config_params
...
>>> register(PersonItem)
>>> PersonItem.get_config()
{'is_human': <True, Bool>, 'age': <<class 'merengue.registry.params.NOT_PROVIDED'>, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}

# saving registered item in database should change the configuration
>>> reg_item = PersonItem.get_registered_item()
>>> reg_item.config
{u'is_human': True}
>>> reg_item.config['age'] = 30
>>> reg_item.save()
>>> PersonItem.get_config()
{'is_human': <True, Bool>, 'age': <30, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}
>>> del reg_item.config['age']
>>> reg_item.save()
>>> PersonItem.get_config()
{'is_human': <True, Bool>, 'age': <<class 'merengue.registry.params.NOT_PROVIDED'>, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}

# testing get_merged_config

# note that 'age' param should not be updated (because is not provided)
>>> PersonItem.get_merged_config(params.ConfigDict(config_params, {'is_human': False}))
{'is_human': <False, Bool>, 'age': <<class 'merengue.registry.params.NOT_PROVIDED'>, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}
>>> PersonItem.get_merged_config(params.ConfigDict(config_params, {'is_human': False}), params.ConfigDict(config_params, {'age': 20}))
{'is_human': <True, Bool>, 'age': <20, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}

# last dictionary should be which set the 'age' param
>>> PersonItem.get_merged_config(params.ConfigDict(config_params, {'age': 10}), params.ConfigDict(config_params, {'age': 12}))
{'is_human': <True, Bool>, 'age': <12, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}

"""}
