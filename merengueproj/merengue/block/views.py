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

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.utils.simplejson import dumps
from django.utils.translation import ugettext as _

from merengue.block.forms import BlockConfigForm
from merengue.block.models import RegisteredBlock
from merengue.perms.utils import has_global_permission


def blocks_index(request):
    """ block index marker (not implemented) """
    return ''


def blocks_reorder(request):
    def relocate_blocks(items, cls):
        for order, item in enumerate(items):
            if "#" in item:
                item_split = item.split("#")
                element_id = int(item_split[0])
                placed_at = item_split[1]
                try:
                    cls.objects.get(id=element_id,
                                    placed_at=placed_at,
                                    order=order)
                except cls.DoesNotExist:
                    element = cls.objects.get(id=element_id)
                    element.order = order
                    element.placed_at = placed_at
                    element.save()

    mimetype = "application/json"
    if request.is_ajax() and request.POST and "new_order" in request.POST:
        new_order = request.POST['new_order']
        items = new_order.split(",")
        relocate_blocks(items, RegisteredBlock)
        return HttpResponse(dumps(True), mimetype=mimetype)
    return HttpResponseBadRequest(mimetype=mimetype)


def generate_blocks_configuration_for_content(request, block_id):
    try:
        reg_block = RegisteredBlock.objects.get(id=block_id)
        block = reg_block.get_registry_item()
        form = BlockConfigForm()
        form.fields['config'].set_config(block.get_config())
        result = form.as_django_admin()
        result = result.replace('<fieldset class="module aligned">', '')
        result = result.replace('</fieldset>', '')
        result = result.replace('<div class="form-row">', '')
        result = result[::-1].replace('>vid/<', '', 1)[::-1]
        # previous replace just removes the last </div> ocurrence
        result = result.replace(_('Configuration'), _('Block specific configuration'))
        result += '<p class="help">Fill this field to overwrite the block configuration</p>'
    except RegisteredBlock.DoesNotExist:
        result = ''
    return HttpResponse(result, mimetype='text/html')


def generate_blocks_configuration(request, block_id):
    if not has_global_permission(request.user, 'manage_portal'):
        raise PermissionDenied()
    reg_block = RegisteredBlock.objects.get(id=block_id)
    block = reg_block.get_registry_item()
    config = block.get_config()
    if request.method == 'POST':
        form = BlockConfigForm(request.POST)
        form.fields['config'].set_config(config)
        if form.is_valid():
            reg_block.config = form.cleaned_data['config']
            reg_block.save()
            return HttpResponse('ok')
    else:
        form = BlockConfigForm()
        form.fields['config'].set_config(config)
    return render_to_response('blocks/block_config.html', {
        'form': form,
        'reg_block': reg_block,
        'block': block,
    })
