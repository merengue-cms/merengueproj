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
    version = "0.1",
    install_requires = ['django', 'PIL', 'beautifulsoup', 'johnny-cache'],
    author = "Yaco Sistemas",
    author_email = "msaelices@yaco.es",
    description = "Django-based CMS with steroids",
    url = "http://merengueproject.org/",
    #download_url = 'http://merengueproject.org/releases/0.1/merengue-0.1.tar.gz',
    include_package_data = True,

    packages = find_packages(),
    data_files = data_files,
    scripts = ['bin/merengue-admin.py'],
)
