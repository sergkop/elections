from django.conf.urls.defaults import patterns, url

from users.views import ProfileView

urlpatterns = patterns('users.views',
    url(r'^user/(?P<id>\d+)$', ProfileView.as_view(), name='profile'),
    #url(r'^user/(?P<id>\d+)/tasks$', ProfileTasksView.as_view(), name='profile_tasks'),

    url(r'^profile$', 'profile', name='my_profile'),

    url(r'^remove_account$', 'remove_account', name='remove_account'),

    url(r'^send_message$', 'send_message', name='send_message'),
)