#!/usr/bin/env python

import sys
import os
import site


def ask_yesno_question(question, default_answer):
    while True:
        prompt = '%s: (yes/no) [%s]: ' % (question, default_answer)
        answer = raw_input(prompt).strip()
        if answer == '':
            return default_answer == 'yes' and True or False
        elif answer in ('yes', 'no'):
            return answer == 'yes' and True or False
        else:
            print 'Please answer yes or no'


def fix_merengue_links():
    cwd = os.getcwd()
    if os.path.islink(os.path.join(cwd, 'merengue')):
        print "We have detected a broked merengue link in project directory\n"
        fix_links = ask_yesno_question("Do you want to try fix merengue links?", "no")
        if not fix_links:
            sys.exit(1)
        while True:
            merengue_path = raw_input("What is the path to merengueproj directory?: ")
            sys.path.append(merengue_path)
            try:
                import merengue  # pyflakes:ignore
            except ImportError:
                print "In this directory merengue module cannot be imported"
            else:
                break
        merengue_link_path = os.path.join(cwd, 'merengueproj')
        link_src = os.path.realpath(merengue_link_path)
        os.remove(merengue_link_path)
        os.symlink(merengue_path, merengue_link_path)
        print 'Fixing %s, changing from broken "%s" to "%s" location...' % (merengue_link_path, link_src, merengue_path)

try:
    import django  # pyflakes:ignore
except ImportError:
    sys.stderr.write("Error: django cannot be found. Make sure you have django installed and in your python path\n")
    sys.exit(1)

try:
    import merengue  # pyflakes:ignore
except ImportError:
    sys.stderr.write("Error: merengue cannot be found\n")
    fix_merengue_links()

try:
    import settings  # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

from merengue.base.management import execute_manager

path = site.addsitedir(os.path.join(settings.BASEDIR, "libs"), set())
if path:
    sys.path = list(path) + sys.path
sys.path.insert(0, os.path.join(settings.MERENGUEDIR, "apps"))
sys.path.insert(0, os.path.join(settings.BASEDIR, "apps"))


if __name__ == "__main__":
    execute_manager(settings)
