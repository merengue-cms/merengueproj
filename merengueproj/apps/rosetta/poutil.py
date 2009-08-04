import re, string, sys, os
from django.conf import settings
from rosetta import polib
try:
    set
except NameError:
    from sets import Set as set   # Python 2.3 fallback
    
def find_pos(lang, include_djangos = False, include_rosetta = False):
    """
    scans a couple possible repositories of gettext catalogs for the given 
    language code
    
    """
    
    paths = []
    
    # project/locale
    parts = settings.SETTINGS_MODULE.split('.')
    project = __import__(parts[0], {}, {}, [])
    paths.append(os.path.join(os.path.dirname(project.__file__), 'locale'))
    
    # django/locale
    if include_djangos:
        paths.append(os.path.join(os.path.dirname(sys.modules[settings.__module__].__file__), 'locale'))
    
    # settings 
    for localepath in settings.LOCALE_PATHS:
        if os.path.isdir(localepath):
            paths.append(localepath)
    
    # project/app/locale
    for appname in settings.INSTALLED_APPS:
        if 'rosetta' == appname and include_rosetta == False:
            continue
            
        p = appname.rfind('.')
        if p >= 0:
            app = getattr(__import__(appname[:p], {}, {}, [appname[p+1:]]), appname[p+1:])
        else:
            app = __import__(appname, {}, {}, [])

        apppath = os.path.join(os.path.dirname(app.__file__), 'locale')

        if os.path.isdir(apppath):
            paths.append(apppath)
            
    ret = set()
    rx=re.compile(r'(\w+)/../\1')
    langs = (lang,)
    if u'-' in lang:
        _l,_c =  map(lambda x:x.lower(),lang.split(u'-'))
        langs += (u'%s_%s' %(_l, _c), u'%s_%s' %(_l, _c.upper()), )
    elif u'_' in lang:
        _l,_c = map(lambda x:x.lower(),lang.split(u'_'))
        langs += (u'%s-%s' %(_l, _c), u'%s-%s' %(_l, _c.upper()), )
        
    for path in paths:
        for lang_ in langs:
            dirname = rx.sub(r'\1', '%s/%s/LC_MESSAGES/' %(path,lang_))
            for fn in ('django.po','djangojs.po',):
                if os.path.isfile(dirname+fn):
                    ret.add(os.path.abspath(dirname+fn))
    return list(ret)

def pagination_range(first,last,current):
    r = []
    
    r.append(first)
    if first + 1 < last: r.append(first+1)
    
    if current -2 > first and current -2 < last: r.append(current-2)
    if current -1 > first and current -1 < last: r.append(current-1)
    if current > first and current < last: r.append(current)
    if current + 1 < last and current+1 > first: r.append(current+1)
    if current + 2 < last and current+2 > first: r.append(current+2)
    
    if last-1 > first: r.append(last-1)
    r.append(last)
    
    r = list(set(r))
    r.sort()
    prev = 10000
    for e in r[:]:
        if prev + 1 < e:
            try:
                r.insert(r.index(e), '...')
            except ValueError:
                pass
        prev = e
    return r

FUZZY = 'fuzzy'

def priority_merge(po_destination, po_source, priority=False):
    for entry in po_source:
        e = po_destination.find(entry.msgid)

        if e:
            if (not e.translated() or priority) and entry.translated():
                # entry found, we update if it isn't translated
                e.occurrences = entry.occurrences
                e.comment = entry.comment
                e.msgstr = entry.msgstr
                if FUZZY in e.flags:
                    e.flags.remove(FUZZY)
        else:
            # entry is not in the po file, we must add it
            # entry is created with msgid, occurrences and comment
            new_entry = polib.POEntry(msgid=entry.msgid,
                                      occurrences=entry.occurrences,
                                      comment=entry.comment,
                                      msgstr = entry.msgstr)
            po_destination.append(new_entry)
    po_destination.save()


def get_changes(po_source, po_destination, priority):
    l_changes = []
    l_news = []
    for entry_source in po_source:
        entry_destination = po_destination.find(entry_source.msgid)
        item = {}
        if entry_destination:
            if entry_source.translated() and not entry_destination.translated():
                item['entry'] = entry_source
                item['entry_destination'] = ""
            elif priority:
                item['entry'] = entry_source
                item['entry_destination'] = entry_destination.msgstr
                if item:
                    l_changes.append(item)
        else:
            item['entry'] = entry_source
            l_news.append(item)
    return l_changes, l_news
