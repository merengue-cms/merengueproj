from django.utils.translation import ugettext_lazy as _, ugettext

from merengue.block.blocks import Block, BaseBlock
from merengue.registry import params
from merengue.registry.items import BlockQuerySetItemProvider
from merengue.section.models import Document

from plugins.filebrowser.models import Repository


class LatestFilesBlock(BlockQuerySetItemProvider, Block):
    name = 'latestfiles'
    default_place = 'rightsidebar'
    verbose_name = _('Latest Files Block')
    help_text = _('Block that represents a list of recent files of the filebrowser')

    config_params = BaseBlock.config_params + BlockQuerySetItemProvider.config_params + [
        params.PositiveInteger(
            name='limit',
            label=_('number of files for the "Latest Files" block'),
            default=3,
        ),
        params.Single(
            name='mainrepo',
            label=_('Name of the repository to show files from it'),
            default='',
        ),
        params.Bool(
            name='filtering_document',
            label=_('If the repository name is equal to document slug, filter for the files of this repository'),
            default=False,
        ),
    ]

    default_caching_params = {
        'enabled': False,
        'timeout': 3600,
        'only_anonymous': True,
        'vary_on_user': False,
        'vary_on_url': True,
        'vary_on_language': True,
    }

    def get_contents(self, request=None, context=None, section=None):
        repos = Repository.objects.all()
        return repos

    def queryset(self, request=None, context=None, section=None):
        queryset = self.get_contents(request, context, section)
        content = context.get('content', None)
        document = isinstance(content, Document) and content

        if section and self.get_config().get('filtering_section', False).get_value():
            queryset = queryset.filter(section=section)
        if self.get_config().get('filtering_document', False).get_value() and \
           document and queryset.filter(name=document.slug):
            queryset = queryset.filter(name=document.slug)
        return queryset

    def render(self, request, place, context, *args, **kwargs):
        repolist = self.get_queryset(request, context)
        limit = self.get_config().get('limit').get_value()
        mainrepo = self.get_config().get('mainrepo').get_value()
        main = None
        if mainrepo:
            try:
                main = repolist.get(name=mainrepo)
            except Repository.DoesNotExist:
                pass
        if main:
            files = main.latest_files(limit)
        else:
            if not repolist:
                return ''
            files = []
            for repo in repolist:
                files += repo.latest_files(limit)
        if not files:
            return ''
        files = sorted(files, key=lambda f: f.modificated, reverse=True)[:limit]
        return self.render_block(request,
                                 template_name='filebrowser/blocks/latestfiles.html',
                                 block_title=ugettext('Downloads'),
                                 context={'files': files,
                                          })
