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
            if not i.endswith('.metadata') and os.path.exists(os.path.join(join(root, path), i)):
                childs.append(i)
        self.childnumber = len(childs)
        if not self.path.endswith('/'):
            self.path += '/'


class FileDesc(PathDesc):
    """ File descriptor class """

    def __init__(self, root, path, repo=None):
        super(FileDesc, self).__init__(root, path)
        metadata_name = os.path.join(root, path + '.metadata')
        self.repository = repo
        if os.path.exists(metadata_name):
            metadata_file = open(metadata_name, 'r')
            metadata = metadata_file.read()
            metadata_file.close()
            metadata_lines = metadata.split('\n')
            self.title = metadata_lines[0]
            self.description = '\n'.join(metadata_lines[2:])
        else:
            self.title = ''
            self.description = ''
