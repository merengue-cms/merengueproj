# Copyright (c) 2010 by Yaco Sistemas <msaelices@yaco.es>
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

import os
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

data_files = []
for dirpath, dirnames, filenames in os.walk('.'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = "merengue",
    version = "0.6.0-alpha1",
    install_requires = ['django==1.1.2', 'PIL', 'BeautifulSoup', 'south==0.7.2', 'pexpect',
                        'django-extensions==0.5', 'cssutils', 'django-tagging', 'django-pagination',
                        'template_utils', 'django-mptt', 'encutils', 'django-oembed',
                        'django-ajax-selects', 'django-threadedcomments==0.5.3',
                        'django-notification==0.1.5', 'django-oot', 'django-genericforeignkey',
                        'django-stdfile', 'cmsutils', 'transhette', 'django-inlinetrans',
                        'django-transmeta', ],
    author = "Yaco Sistemas",
    author_email = "msaelices@yaco.es",
    description = "Django-based CMS with steroids",
    url = "http://www.merengueproject.org/",
    #download_url = 'http://www.merengueproject.org/download/0.5/merengue-0.5.tar.gz',
    include_package_data = True,
    classifiers = [
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Programming Language :: Python',
    ],
    packages = find_packages(),
    data_files = data_files,
    scripts = ['bin/merengue-admin.py'],
)
