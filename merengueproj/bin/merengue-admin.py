#!/usr/bin/env python

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

import sys

from os import path

try:
    from merengue.base import management
except ImportError:
    # try adding parent directory (merengueproj directory) to PYTHONPATH
    parent_dir = path.join(path.dirname(path.abspath(__file__)), path.pardir)
    sys.path.insert(0, parent_dir)
    from merengue.base import management


if __name__ == "__main__":
    management.execute_from_command_line()
