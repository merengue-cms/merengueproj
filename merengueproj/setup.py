import os
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

data_files = []
for dirpath, dirnames, filenames in os.walk('.'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = "merengue",
    version = "0.5",
    install_requires = ['django==1.1.2', 'PIL', 'beautifulsoup'],
    author = "Yaco Sistemas",
    author_email = "msaelices@yaco.es",
    description = "Django-based CMS with steroids",
    url = "http://www.merengueproject.org/",
    #download_url = 'http://www.merengueproject.org/download/0.5/merengue-0.5.tar.gz',
    include_package_data = True,
    classifiers = [
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
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
