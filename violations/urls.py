from django.conf.urls.defaults import *

urlpatterns = patterns('violations.views',
    url(r'^(?P<violation_id>\d+)$', 'violation_view', name='violation_view'),
    url(r'^report$', 'report_violation', name='report_violation'),
)
