#!/usr/bin/env python
import sys
import os
import site
from merengue.base.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

path = site.addsitedir(os.path.join(settings.BASEDIR, "libs"), set())
if path:
    sys.path = list(path) + sys.path
sys.path.insert(0, os.path.join(settings.BASEDIR, "apps"))
sys.path.insert(0, os.path.join(settings.BASEDIR, "projapps"))


if __name__ == "__main__":
    execute_manager(settings)
