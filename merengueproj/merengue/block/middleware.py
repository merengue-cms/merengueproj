from django.http import HttpResponse


class RenderBlockMiddleware(object):
    """This middleware render only a block if passed by request """

    def process_request(self, request):
        if 'render_block' in request.GET:
            from merengue.block.models import RegisteredBlock, BlockContentRelation

            block_id = request.GET['render_block']
            related = 'related' in request.GET
            if not related:
                reg_block = RegisteredBlock.objects.get(id=block_id)
                place = reg_block.placed_at
                bcr = None
            else:
                bcr = BlockContentRelation.objects.get(id=block_id)
                reg_block = bcr.block
                place = bcr.placed_at
            block = reg_block.get_registry_item_class()
            return HttpResponse(block.render(
                request,
                place=place,
                context=dict(),
                block_content_relation=bcr,
            ))
