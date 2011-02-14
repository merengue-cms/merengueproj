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

from merengue.registry import params
from merengue.registry.items import RegistrableItem


config_params = [
    params.Bool(name='is_human', default=True),
    params.Integer(name='age'),
    params.List(name='friends', choices=('Juan', 'Luis', 'Pepe'))
]


class PersonItem(RegistrableItem):
    config_params = config_params


class SingletonItem(RegistrableItem):
    singleton = True
    config_params = config_params


__test__ = {"doctest": """
>>> from merengue.registry import register

>>> config_params
[<True, Bool>, <<class 'merengue.registry.params.NOT_PROVIDED'>, Integer>, <<class 'merengue.registry.params.NOT_PROVIDED'>, List>]
>>> config = params.ConfigDict(config_params, {'age': 25, 'friends': ('Juan', )})
>>> config
{'is_human': <True, Bool>, 'age': <25, Integer>, 'friends': <('Juan',), List>}
>>> config.update(params.ConfigDict(config_params, {'age': 40}))
>>> config
{'is_human': <True, Bool>, 'age': <40, Integer>, 'friends': <('Juan',), List>}

>>> reg_item = register(PersonItem)
>>> item = reg_item.get_registry_item()
>>> item.get_config()
{'is_human': <True, Bool>, 'age': <<class 'merengue.registry.params.NOT_PROVIDED'>, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}

# saving registered item in database should change the configuration
>>> reg_item.config
{'is_human': True}
>>> reg_item.config['age'] = 30
>>> reg_item.save()
>>> item.get_config()
{'is_human': <True, Bool>, 'age': <30, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}
>>> del reg_item.config['age']
>>> reg_item.save()
>>> item.get_config()
{'is_human': <True, Bool>, 'age': <<class 'merengue.registry.params.NOT_PROVIDED'>, Integer>, 'friends': <<class 'merengue.registry.params.NOT_PROVIDED'>, List>}

# testing singleton objects

>>> register(PersonItem)
<RegisteredItem: PersonItem>
>>> register(PersonItem)   # we can register PersonItem twice
<RegisteredItem: PersonItem>

>>> register(SingletonItem)
<RegisteredItem: SingletonItem>
>>> register(SingletonItem)  # SingletonItem is a singleton... it cannot be registered twice
Traceback (most recent call last):
    ...
AlreadyRegistered: item class "<class 'merengue.registry.tests.SingletonItem'>" is already registered

"""}
