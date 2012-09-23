# -*- coding:utf-8 -*-
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse

from locations.models import Location
from services.cache import cache_function
from users.models import CommissionMember, Profile, WebObserver

# TODO: include it in info and cache (?)
def regions_list(location=None):
    """ location = None for Russia """
    if location is None:
        regions = [('', u'Выбрать субъект РФ'), None, None, None] # reserve places for Moscow, St. Petersburg and foreign countries
        for loc_id, name in Location.objects.filter(region=None).order_by('name').values_list('id', 'name'):
            if name == u'Москва':
                regions[1] = (loc_id, name)
            elif name == u'Санкт-Петербург':
                regions[2] = (loc_id, name)
            else:
                regions.append((loc_id, name))
        return regions
    elif location.is_region():
        return list(Location.objects.filter(region=location, tik=None).order_by('name').values_list('id', 'name'))
    elif location.is_tik():
        return list(Location.objects.filter(tik=location).order_by('name').values_list('id', 'name'))
    else:
        return []

# TODO: introduce query generators for other types of counting
def get_roles_query(location=None):
    if location is None:
        return Q()

    query = Q(location=location)
    if location.is_region():
        query |= Q(location__region=location)
    #elif location.is_tik():
    #    query |= Q(location__tik=location)

    return query

# TODO: include it in info and cache
# TODO: count members differently?
def get_roles_counters(location=None):
    counters = {}
    query = get_roles_query(location)

    def filter_inactive_users(queryset):
        return queryset.exclude(user__user__email='').filter(user__user__is_active=True)

    #roles = list(filter_inactive_users(Role.objects.filter(query)).values_list('type', 'user'))

    #for role_type in ROLE_TYPES:
    #    counters[role_type] = len(filter(lambda r: r[0]==role_type, roles))

    # TODO: do it for location=None only?
    counters['total'] = Profile.objects.exclude(user__email='').filter(user__is_active=True).count()

    # TODO: use count here?
    counters['web_observer'] = len(filter_inactive_users(WebObserver.objects.filter(query)) \
            .distinct().values_list('user', flat=True))

    counters['commission_members'] = CommissionMember.objects.filter(query).count()

    return counters

def get_locations_data(queryset, level):
    """ level=2,3,4 """
    js = 'var electionCommissions = { '
    data = []

    # get all locations from higher levels as well
    if level == 2:
        queryset = queryset.filter(region=None)
    elif level == 3:
        queryset = queryset.filter(tik=None)

    # TODO: limit locations number according to the level (don't get uiks for the whole country at once)
    locations = list(queryset.only('id', 'x_coord', 'y_coord', 'region', 'tik', 'name', 'address', 'data'))

    # TODO: уровень 3: delta_x=20, delta_y=10 уровень 4: 1,8 и 0,9

    for location in locations:
        if location.x_coord:
            js += str(location.id) + ': ' + location.map_data() + ','

    js = js[:-1] + '};'

    return HttpResponse(js, mimetype='application/javascript')
