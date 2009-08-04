def section(request):
    # simplest context processor ever :-)
    return {'section': request.section}
