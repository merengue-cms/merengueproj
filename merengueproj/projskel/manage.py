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
                import merengue
            except ImportError:
                print "In this directory merengue module cannot be imported"
            else:
                break
        for d, subdirs, files in os.walk(cwd):
            for f in files:
                filepath = os.path.join(cwd, d, f)
                if os.path.islink(filepath) and os.path.lexists(filepath): # is a broken link
                    fixlink(filepath, merengue_path)


def fixlink(filepath, merengue_path):
    link_src = os.path.realpath(filepath)
    index = link_src.find('merengueproj') + len('merengueproj')
    new_link_src = link_src.replace(link_src[0:index], merengue_path.rstrip('/'))
    if new_link_src != link_src:
        print 'Fixing %s, changing from broken "%s" to "%s" location...' % (filepath, link_src, new_link_src)
        os.remove(filepath)
        os.symlink(new_link_src, filepath)

try:
    import django
except ImportError:
    sys.stderr.write("Error: django cannot be found. Make sure you have django installed and in your python path\n")
    sys.exit(1)

try:
    import merengue
except ImportError:
    sys.stderr.write("Error: merengue cannot be found\n")
    fix_merengue_links()

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

from merengue.base.management import execute_manager

path = site.addsitedir(os.path.join(settings.BASEDIR, "libs"), set())
if path:
    sys.path = list(path) + sys.path
sys.path.insert(0, os.path.join(settings.BASEDIR, "apps"))
sys.path.insert(0, os.path.join(settings.BASEDIR, "projapps"))


if __name__ == "__main__":
    execute_manager(settings)
