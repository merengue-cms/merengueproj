from django.http import HttpResponse


class RenderBlockMiddleware(object):
    """This middleware render only a block if passed by request """

    def process_request(self, request):
        if 'render_block' in request.GET:
            from merengue.block.models import RegisteredBlock

            block_id = request.GET['render_block']
            reg_block = RegisteredBlock.objects.get(id=block_id)
            place = reg_block.placed_at
            block = reg_block.get_registry_item()
            return HttpResponse(block.render(
                request,
                place=place,
                context=dict(),
            ))
