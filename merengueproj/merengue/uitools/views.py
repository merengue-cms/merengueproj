from inplaceeditform.views import save_ajax

from merengue.block.models import RegisteredBlock


def merengue_save_ajax(request):
    httpresponse = save_ajax(request)
    registered_block_id = request.POST.get('block_id', None)
    if registered_block_id:
        registered_block = RegisteredBlock.objects.get(pk=registered_block_id)
        block = registered_block.get_registry_item()
        block.invalidate_cache()
    return httpresponse
