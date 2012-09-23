from django.conf.urls.defaults import *

from locations.views import *

urlpatterns = patterns('locations.views',
    url(r'^(?P<loc_id>\d+)$', InfoView.as_view(), name='location_info'),
    url(r'^(?P<loc_id>\d+)/wall$', WallView.as_view(), name='location_wall'),
    #url(r'^(?P<loc_id>\d+)/map$', 'location_view', name='location_map', kwargs={'view': 'location_map'}),
    url(r'^(?P<loc_id>\d+)/web_observers', WebObserversView.as_view(), name='web_observers', kwargs={'view': 'web_observers'}),
    url(r'^(?P<loc_id>\d+)/participants', ParticipantsView.as_view(), name='participants', kwargs={'view': 'participants'}),

    # Redirect, not used anymore
    url(r'^(?P<loc_id>\d+)/supporters', 'location_supporters', name='supporters'),

    url(r'^get_subregions$', 'get_subregions', name='get_subregions'),
    url(r'^goto_location$', 'goto_location', name='goto_location'),

    url(r'^locations_data$', 'locations_data', name='locations_data'),
)
