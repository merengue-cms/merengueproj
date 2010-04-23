VERSION = (0, 5, 0, 'alpha', 0)


def get_version():
    """ Taked from django one. Merengue will use same version scheme """
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = '%s %s %s' % (version, VERSION[3], VERSION[4])
    from os import path
    from django.utils.version import get_svn_revision
    svn_rev = get_svn_revision(path.dirname(path.abspath(__file__)))
    if svn_rev != u'SVN-unknown':
        version = "%s %s" % (version, svn_rev)
    return version
