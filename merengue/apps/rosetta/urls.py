from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('rosetta.views',
    url(r'^$', 'home', name='rosetta-home'),
    url(r'^restart/$', 'restart_server', name='rosetta-restart-server'),
    url(r'^apply_changes/$', 'do_restart', name='apply_changes'),
    url(r'^pick/$', 'list_languages', name='rosetta-pick-file'),
    url(r'^download/$', 'download_file', name='rosetta-download-file'),
    url(r'^select/(?P<langid>[\w\-]+)/(?P<idx>\d+)/$', 'lang_sel', name='rosetta-language-selection'),
    url(r'^set_new_translation/$', 'set_new_translation', name='set_new_translation'),
    url(r'^inline_demo/$', 'inline_demo', name='inline_demo'),
    url(r'^regenerate_translations/$', 'regenerate_translations', name='regenerate_translations'),
    url(r'^update/confirmation/$', 'update_confirmation', name='rosetta-confirmation-file'),
    url(r'^update/file/((?P<no_confirmation>\w+)/)?$', 'update', name='rosetta-update-file'),
    url(r'^update/catalogue/((?P<no_confirmation>\w+)/)?$', 'update_catalogue', name='rosetta-update-catalogue'),
    url(r'^change/catalogue/$', 'change_catalogue', name='rosetta-change-catalogue'),
    url(r'^ajax/$', 'ajax', name='rosetta-ajax'),
)
