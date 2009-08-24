from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('merengue.section.views',
    url(r'ajax/get_search_filters_and_options/$', 'get_search_filters_and_options', name='get_search_filters_and_options'),
    url(r'^(?P<section_slug>[\w-]+)/$', 'section_view', name='section_view'),
    url(r'^(?P<section_slug>[\w-]+)/crear-documento-principal/$', 'create_and_link_document', name='create_and_link_document'),
    url(r'^(?P<section_slug>[\w-]+)/css/$', 'section_custom_style', name='section_custom_style'),
    url(r'^(?P<section_slug>[\w-]+)/(?P<document_slug>[\w-]+)/$', 'document_view', name='document_view'),
)


def section_patterns(section_slug, name, prefix='', context={}):
    _patterns = agenda_patterns(section_slug, name, prefix, context) + \
                 docs_patterns(section_slug, name, prefix, context)
    return _patterns


def docs_patterns(section_slug, name, prefix='', context={}, **kwargs):
    kwargs_param = {'section_slug': section_slug, 'original_context': context}
    kwargs_param.update(kwargs)
    return patterns('section.views',
        url(r'^%s(?P<document_slug>[\w-]+)/$' % prefix, 'document_view',
            kwargs=kwargs_param,
            name='%s_document_view' % name),
    )


def agenda_patterns(section_slug, name, prefix='', context={}):
    return patterns('section.views',
        url(r'^%sagenda/$' % prefix, 'section_agenda',
            kwargs={'section_slug': section_slug, 'original_context': context},
            name='%s_agenda_view' % name),
    )
