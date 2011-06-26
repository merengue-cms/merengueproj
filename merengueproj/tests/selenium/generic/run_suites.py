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
import shutil
from optparse import OptionParser


def run_all_suite():
    usage = "usage: %prog [options] url_base"
    parser = OptionParser(usage)
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
    parser.add_option('-f', '--firefox-profile-directory', action='store', dest='firefox_profile',
                        help="Use a firefox profile directory")
    parser.add_option('-s', '--selenium-server', action='store', dest='selenium_server',
                        help="Selenium server path")
    parser.add_option('--display', action='store', dest='display', type='int',
                        help='Display number for framebuffer.')

    (options, args) = parser.parse_args()

    directory_list = [i for i in os.listdir('.') if os.path.isdir(i) \
                          and not i.startswith('.') \
                          and 'suite.html' in os.listdir(i)]
    if len(args) != 1:
        parser.error("You need to define a base URL to launch the test "
                     "(i.e. http://localhost:8000/)""")
    pwd = os.path.dirname(os.path.abspath(__file__))
    extensions_file = os.path.join(os.path.abspath('..'), 'extensions', 'user-extensions.js')
    if options.selenium_server:
        selenium_file = options.selenium_server
    else:
        selenium_file = os.path.join(pwd, 'selenium-server.jar')
    variables_file = os.path.join(pwd, 'variables.html')
    if options.firefox_profile:
        firefox_arg = '-firefoxProfileTemplate "%s"' % options.firefox_profile
    else:
        firefox_arg = ''
    if os.path.exists(extensions_file) and os.path.exists(selenium_file):
        for directory in directory_list:
            os.chdir(pwd)
            directory_path = os.path.join(pwd, directory)
            suite_file = os.path.join(directory_path, 'suite.html')
            results_file = os.path.join(pwd, 'results', directory + '.html')
            variables_copy = os.path.join(directory_path, 'variables.html')
            shutil.copy(variables_file, variables_copy)
            if options.verbose:
                print 'Launching Selenium RC in %s test suite...' % suite_file
            cmd = 'java -jar %s -htmlSuite "*firefox" "%s" "%s" "%s" -userExtensions "%s" %s' % (
                selenium_file,
                args[0],
                suite_file,
                results_file,
                extensions_file,
                firefox_arg,
            )
            if options.display:
                cmd = 'DISPLAY=:%s %s' % (options.display, cmd)
            os.system(cmd)
            os.remove(variables_copy)
    else:
        print 'ERROR: File selenium-server.jar/user-extensions.js can not be found.'

if __name__ == '__main__':
    run_all_suite()
