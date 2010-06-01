from merengue.section.views import section_view


def microsite_view(request, microsite_slug):
    return section_view(request, microsite_slug)
