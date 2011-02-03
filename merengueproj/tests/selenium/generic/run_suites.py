#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright (c) 2010 by Yaco Sistemas
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
import sys


def run_all_suite():
    directory_list = [i for i in os.listdir('.') if os.path.isdir(i) \
                          and not i.startswith('.') \
                          and 'suite.html' in os.listdir(i)]
    if len(sys.argv) == 1:
        print """
ERROR: Can not found base url.
USE: python run_suites.py 'url base for selenium test, as http://localhost:8000/'
"""
    else:
        if 'selenium-server.jar' in os.listdir('.') and 'user-extensions.js' in os.listdir('.'):
            for directory in directory_list:
                os.system('java -jar selenium-server.jar -htmlSuite "*firefox" "%s" "%s" "%s" -userExtensions "%s"' \
                              % (sys.argv[1],
                                 os.path.join(os.path.abspath(directory), 'suite.html'),
                                 os.path.join(os.path.abspath('.'), 'results', directory + '.html'),
                                 os.path.join(os.path.abspath('.'), 'user-extensions.js')))
        else:
            print 'ERROR: File selenium-server.jar/user-extensions.js can not be found.'

if __name__ == '__main__':
    run_all_suite()
