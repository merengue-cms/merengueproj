#!/usr/bin/env python
from __future__ import with_statement # needed for python 2.5

import os
import sys

from fabric.api import *
from fabric.contrib.console import confirm

# ================================================================
# NOTE:
#    using this fabfile expects that you have the python utility
# fabric installed locally.
# ================================================================

# GLOBALS

env.path = '/tmp'
env.project_name = 'merengue'

# ENVIRONMENTS


def linode():
    """
    Configure for the host at linode.
    """
    env.hosts = ['localhost']
    env.user_home = os.getenv("HOME")

# COMMANDS


def compilation_error():
    confirm("""Error compiling. Maybe the building tools and
            Python development headers are not installed. \n
            Do you want to continue installation?""")


def background_setup():
    require('hosts', provided_by=[linode])
    pip_install('ipython')
    with settings(warn_only=True):
        result = pip_install('PIL')
        if result.failed:
            compilation_error()
    pip_install('beautifulsoup')
    pip_install('simplejson')
    pip_install('http://geopy.googlecode.com/svn/trunk/')
    pip_install('django')
    pip_install('johnny-cache')


def database_menu():
    return prompt("""Which database management system would you like to use?
                        1) PostgreSQL (default)
                        2) MySQL
                        3) sqlite
                    """, default='1')


def database_setup():
    option = database_menu()
    with settings(warn_only=True):
        if option == '1' or '':
            result = pip_install('psycopg2')
            if result.failed:
                compilation_error()
            else:
                return 'postgresql_psycopg2'
        elif option == '2':
            result = pip_install('MySQL-python')
            if result.failed:
                compilation_error()
            else:
                return 'mysql'
        elif option == '3':
            return 'sqlite3'
        else:
            print 'Warning: Invalid option selected. No connector will be installed'
            return 'sqlite3'
    abort("Database connector installation failed")


def production_mode_setup():
    pass


def create_db(project_name, postgis_enabled):
    ''' Creating postgresql database '''
    sudo('createuser -s %s' % project_name, user='postgres')
    if postgis_enabled:
        sudo("createdb -T template_postgis %s" % project_name, user='postgres')
    else:
        sudo('createdb %s' % project_name, user='postgres')
    sudo('psql -c "ALTER USER myproject WITH encrypted password \'%s\';"'
        % project_name, user='postgres')


def virtualenv_setup():
    installation_dir = prompt("Enter a installation directory",
                            default="%s/%s" % (env.user_home,
                                                env.project_name))
    env_name = prompt("Enter a virtual environment name.", default='myvirtenv')
    run("mkdir -p %s" % installation_dir)
    with settings(warn_only=True) and cd(installation_dir):
        result = run("virtualenv --no-site-packages %s" % env_name)
        if result.failed:
            abort("Could not execute virtualenv. Is the package installed?")
    with cd("%s/%s" % (installation_dir, env_name)):
        background_setup()
        svn_checkout("http://svnpub.yaco.es/merengue/trunk/merengueproj")
        settings_file = os.path.join(installation_dir, env_name,
                                    'merengueproj', 'merengue', 'settings.py')
        database_engine = database_setup()
        if database_engine == 'postgresql_psycopg2':
            postgis_enabled = gis_extension_setup(settings_file)
        if confirm('Do you want to create a project?'):
            project_name = prompt('Enter project name', default='myproject')
            run('%s startproject %s --develop'
                % (os.path.join('.', 'merengueproj',
                                'bin', 'merengue-admin.py'),
                    project_name))
            replace_in_file(os.path.join(installation_dir, env_name,
                                            project_name, 'settings.py'),
                                [("DATABASE_NAME = ''",
                                    "DATABASE_NAME = '%s'" % project_name),
                                ("DATABASE_USER = ''",
                                    "DATABASE_USER = '%s'" % project_name),
                                ("DATABASE_PASSWORD = ''",
                                    "DATABASE_PASSWORD = '%s'" % project_name),
                                ("DATABASE_ENGINE = ''",
                                    "DATABASE_ENGINE = '%s'" % database_engine),
                                ("DATABASE_USER = ''",
                                    "DATABASE_USER = '%s'" % project_name)])
        create_db(project_name, postgis_enabled)


def svn_checkout(repository):
    return run("svn co --non-interactive %s" % repository)


def django_setup():
    require('hosts', provided_by=[linode])
    require('user_home', provided_by=[linode])
    try:
        import django
    except ImportError:
        svn_dir = '%(user_home)s/src/SVN' % env
        local('mkdir -p %s' % svn_dir)
        with cd(svn_dir):
            local('svn co ' +
                'http://code.djangoproject.com/svn/django/tags/releases/1.1 ' +
                ' django_src')
        site_packages_dir = get_site_packages_dir()
        sudo('ln -s %s/django_src/django  %s/django' % (svn_dir, site_packages_dir))
        sudo('update-alternatives --install /usr/local/bin/django-admin.py ' +
            'django-admin.py %s/django/bin/django-admin.py 10'
            % site_packages_dir)
        sudo('update-alternatives --install /usr/local/bin/compile-messages.py  ' +
            'compile-messages.py %s/django/bin/compile-messages.py 10'
            % site_packages_dir)
        sudo('update-alternatives --install /usr/local/bin/make-messages.py ' +
            ' make-messages.py %s/django/bin/make-messages.py 10'
            % site_packages_dir)


def gis_extension_setup(settings_file):
    if confirm('Do you want to enable PostGIS Extensions?'):
        replace_in_file(settings_file, [("USE_GIS = False", "USE_GIS = True")])
        return True
    return False


def replace_in_file(filename, replacements):
    try:
        f = open(filename, 'r')
        text = f.read()
        f.close()
    except IOError:
        print "Error reading file %s" % filename
    for replacement in replacements:
        text = text.replace(replacement[0], replacement[1])
    try:
        f = open(filename, 'w')
        f.write(text)
        f.close()
    except IOError:
        print "Error writing file %s" % filename

# UTILITIES


def pip_install(package):
    """
    Install a single package on the remote server with pip.
    """
    return with_virtualenv('pip install %s' % package)


def with_virtualenv(command):
    """
    Executes a command in this project's virtual environment.
    """
    return run('source bin/activate && %s' % command)


def install_merengue():
    linode()
    virtualenv_setup()
