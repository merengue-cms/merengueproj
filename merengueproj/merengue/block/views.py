# Copyright (c) 2010 by Yaco Sistemas
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

from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.importlib import import_module
from django.utils.simplejson import dumps

from merengue.block.forms import BlockConfigForm
from merengue.block.models import RegisteredBlock


def blocks_reorder(request):
    mimetype = "application/json"
    if request.is_ajax() and request.POST and "new_order" in request.POST:
        new_order = request.POST['new_order']
        items = new_order.split(",")
        for order, item in enumerate(items):
            if "#" in item:
                item_split = item.split("#")
                block_id = int(item_split[0])
                placed_at = item_split[1]
                block = RegisteredBlock.objects.get(id=block_id)
                block.order = order
                block.placed_at = placed_at
                block.save()
        return HttpResponse(dumps(True), mimetype=mimetype)
    return HttpResponseBadRequest(mimetype=mimetype)


def generate_blocks_configuration(request, block_id):
    try:
        reg_block = RegisteredBlock.objects.get(id=block_id)
        block = getattr(import_module(reg_block.module), reg_block.class_name)
        form = BlockConfigForm()
        form.fields['config'].set_config(block.get_config())
        result = form.as_django_admin()
        result = result.replace('<fieldset class="module aligned">', '')
        result = result.replace('</fieldset>', '')
        result = result.replace('<div class="form-row">', '')
        result = result[::-1].replace('>vid/<', '', 1)[::-1]
        # previous replace just removes the last </div> ocurrence
        result = result.replace('Config:', 'Block specific configuration:')
        result += '<p class="help">Fill this field to overwrite the block configuration</p>'
    except RegisteredBlock.DoesNotExist:
        result = ''

    return HttpResponse(result, mimetype='text/html')
