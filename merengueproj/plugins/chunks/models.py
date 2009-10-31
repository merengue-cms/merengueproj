from django.db import models
from django.utils.translation import gettext_lazy as _

from transmeta import TransMeta
from merengue.block.models import PLACES
from plugins.chunks.managers import ChunksManager


class Chunk(models.Model):
    """
    A Chunk is a piece of content associated
    with a unique key that can be inserted into
    any template with the use of a special template
    tag
    """
    __metaclass__ = TransMeta


    key = models.CharField(verbose_name=_('key'),
                           help_text="A unique name for this chunk of content",
                           max_length=255,
                           blank=False, unique=True)
    content = models.TextField(_('content'), blank=True, null=True)
    url_patterns = models.TextField(_('url patterns'), blank=True, null=True)
    PLACES_DICT = dict(PLACES)
    if 'all' in PLACES_DICT:
        del PLACES_DICT['all']
    placed_at = models.CharField(max_length=100, choices=tuple(PLACES_DICT.items()), blank=True, null=True)

    objects = ChunksManager()

    class Meta:
        verbose_name = _('chunk')
        verbose_name_plural = _('chunks')
        translate = ('content', )

    def __unicode__(self):
        return unicode(self.key)

    def match_with_url(self, url_query):
        url_patterns = self.url_patterns.replace('\r\n', '\n').split('\n')
        import re
        match = None
        for url_pattern in url_patterns:
            pattern = re.compile(r'%s' % url_pattern)
            match = pattern.match(url_query)
            if match:
                break
        return match
