from django.conf.urls.defaults import *

from locations.views import *

urlpatterns = patterns('locations.views',
    url(r'^(?P<loc_id>\d+)$', InfoView.as_view(), name='location_info'),
    url(r'^(?P<loc_id>\d+)/wall$', WallView.as_view(), name='location_wall'),
    url(r'^(?P<loc_id>\d+)/elections', ElectionsView.as_view(), name='location_elections'),
    url(r'^(?P<loc_id>\d+)/web_observers', WebObserversView.as_view(), name='web_observers'),
    url(r'^(?P<loc_id>\d+)/participants', ParticipantsView.as_view(), name='location_participants'),
    url(r'^(?P<loc_id>\d+)/violations', ViolationsView.as_view(), name='location_violations'),

    url(r'^get_subregions$', 'get_subregions', name='get_subregions'),
    url(r'^goto_location$', 'goto_location', name='goto_location'),

    url(r'^add_commission_member$', 'add_commission_member', name='add_commission_member'),
)
