#!/usr/bin/env python

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
