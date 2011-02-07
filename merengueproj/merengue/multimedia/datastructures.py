from BeautifulSoup import BeautifulSoup


class MediaList(list):

    def __init__(self, namespace):
        self._namespace = namespace
        super(MediaList, self).__init__()

    def append(self, obj):
        if obj not in self:
            super(MediaList, self).append(obj)

    def render(self):
        soup = BeautifulSoup('\n'.join(self))
        media_assets = []
        for node in soup.findAll():  # remove duplicated media assets
            media = unicode(node)
            if media not in media_assets:
                media_assets.append(media)
        return '\n'.join(media_assets)


class MediaDictionary(dict):
    """
    A media dictionary which auto fills itself instead of raising key errors.
    """

    def __init__(self):
        super(MediaDictionary, self).__init__()

    def __getitem__(self, item):
        if item not in self:
            self[item] = MediaList(item)
        return super(MediaDictionary, self).__getitem__(item)
