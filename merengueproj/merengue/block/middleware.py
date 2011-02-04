from django.http import HttpResponse

from merengue.block.models import RegisteredBlock


class RenderBlockMiddleware(object):
    """This middleware render only a block if passed by request """

    def process_request(self, request):
        if 'render_block' in request.GET:
            block_id = request.GET['render_block']
            reg_block = RegisteredBlock.objects.get(id=block_id)
            block = reg_block.get_registry_item_class()
            return HttpResponse(block.render(
                request,
                place=reg_block.placed_at,
                context=None,
                block_content_relation=None,
            ))
