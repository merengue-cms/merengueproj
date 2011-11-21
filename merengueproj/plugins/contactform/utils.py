# Copyright (c) 2011 by Yaco Sistemas <pmartin@yaco.es>
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


import time

from recaptcha.client.captcha import API_SSL_SERVER, API_SERVER


def captcha_displayajaxhtml(public_key, use_ssl=False):
    captcha_id = 'captcha_%s' % ''.join(("%f" % time.time()).split("."))
    if use_ssl:
        server = API_SSL_SERVER
    else:
        server = API_SERVER
    return ('<script type="text/javascript" src="%(ApiServer)s/js/recaptcha_ajax.js"></script>'
            '<script type="text/javascript">'
            '    Recaptcha.create("%(PublicKey)s", "%(CaptchaId)s");'
            '</script>'
            '    <div id="%(CaptchaId)s"></div>' % {
                    'ApiServer': server,
                    'PublicKey': public_key,
                    'CaptchaId': captcha_id,
            })

# And you should be use the similar functions in your callback ajax:

#    * This function create a scripts with src
#    * And returned the embedded scripts
#    var createNodeJS = function(content) {
#        var regex = /<script(?: type=(?:'|")text\/javascript(?:'|"))? (?:src=(?:'|")(.*?)(?:'|"))?[^>]*>([^<]*)<\/script>/gm;
#        var results = regex.exec(content);
#        var evals = [];
#        while(results!= null) {
#            if (results[1] != null) {
#                var script = document.createElement("script");
#                script.setAttribute("src", results[1]);
#                script.setAttribute("type", "text/javascript");
#                document.head.appendChild(script);
#            } else {
#                evals[evals.length] = results[2];
#            }
#            results = regex.exec(content);
#        }
#        return evals;
#    };

#    * This funcion eval the code of the embedded scripts.
#    * This function should be called when the div with CaptchaId and the recaptcha_ajax.js are added to the DOM
#    var evaluateScript = function(evals, i) {
#        var evaluate = function() {
#            while (i < evals.length) {
#                try {
#                    eval(evals[i]);
#                    i++;
#                } catch(err) {
#                    setTimeout(evaluate, 3000);
#                    return 0;
#                }
#            }
#        }
#        evaluate();
#    };

# Example of use:

#    success: function(response) {
#         var evals = createNodeJS(response.description);
#         /* Adding the response.description */
#         evaluateScript(evals, 0);
#    }
