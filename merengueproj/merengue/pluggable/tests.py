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
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from merengue.pluggable import register_plugin


class SimpleTest(TestCase):

    def test_plugin_cache(self):
        """ Test plugin registry """
        from merengue.registry.managers import _registry_lookup_cache
        register_plugin('feedback')
        # the feedback block is empty when registering
        self.assertTrue(('plugins.feedback.blocks.FeedbackBlock', ) not in _registry_lookup_cache._cache)
        self.assertTrue(('plugins.feedback.config.PluginConfig', ) in _registry_lookup_cache._cache and \
                        _registry_lookup_cache._cache[('plugins.feedback.config.PluginConfig', )])
