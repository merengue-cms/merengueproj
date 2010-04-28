from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.simplejson import dumps

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
