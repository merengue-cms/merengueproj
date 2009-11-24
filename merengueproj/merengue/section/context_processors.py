def section(request):
    # simplest context processor ever :-)
    return {'section': getattr(request, 'section', None)}
