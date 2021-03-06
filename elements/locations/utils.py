# -*- coding:utf-8 -*-
from locations.models import Location
from services.cache import cache_function

# TODO: add titles choosing command strings
@cache_function(lambda args, kwargs: 'subregions/'+(str(args[0].id) if len(args)>0 and args[0] else '0'), 500)
def subregion_list(location):
    if location.is_country():
        res = [('', u'Выбрать субъект РФ'), None, None] if location.date is None else [('', u'Выбрать субъект РФ')] # reserve places for Moscow and St. Petersburg
        for loc_id, name in Location.objects.exclude(country=None).filter(region=None, date=location.date if location else None).order_by('name').values_list('id', 'name'):
            if location.date is None:
                if name == u'Москва':
                    res[1] = (loc_id, name)
                elif name == u'Санкт-Петербург':
                    res[2] = (loc_id, name)
                else:
                    res.append((loc_id, name))
            else:
                res.append((loc_id, name))
        return res
    elif location.is_region():
        res = list(Location.objects.filter(region=location, tik=None, date=location.date)
                .order_by('name').values_list('id', 'name'))
        if res:
            res.insert(0, ('', u'Выбрать район'))
        return res
    elif location.is_tik():
        res = list(Location.objects.filter(tik=location, date=location.date).order_by('name').values_list('id', 'name'))
        if res:
            res.insert(0, ('', u'Выбрать УИК'))
        return res
    else:
        return []

def breadcrumbs_context(location):
    query = {}
    query.update({'region__name': location.region.name} if location.region else {'region': None})
    query.update({'tik__name': location.tik.name} if location.tik else {'tik': None})

    related_locations = Location.objects.filter(name=location.name, **query)

    # Get location to which comments, commission members are attached
    if location.is_uik():
        data_location = location
    else:
        r_locs = filter(lambda loc: loc.date is None, related_locations)
        data_location = r_locs[0] if len(r_locs)>0 else location

    return {
        'location': location,
        'subregions': subregion_list(location),
        'related_locations': related_locations,
        'data_location': data_location,
    }
