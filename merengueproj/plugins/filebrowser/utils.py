import os
from os.path import join, basename
from datetime import datetime


class PathDesc(object):
    """ Path Descriptor. Parent class of directory and file descriptor """

    def __init__(self, root, path):
        self.root = root
        self.path = path
        self.name = basename(path)
        stat = os.stat(join(root, path))
        self.size = stat.st_size
        self.modificated = datetime.fromtimestamp(stat.st_mtime)


class DirDesc(PathDesc):
    """ Directory descriptor """

    def __init__(self, root, path):
        super(DirDesc, self).__init__(root, path)
        childs = []
        for i in os.listdir(join(root, path)):
            if os.path.exists(os.path.join(join(root, path), i)):
                childs.append(i)
        self.childnumber = len(childs)
        if not self.path.endswith('/'):
            self.path += '/'


class FileDesc(PathDesc):
    """ File descriptor class """

    def __init__(self, root, path):
        super(FileDesc, self).__init__(root, path)
