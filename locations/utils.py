# -*- coding:utf-8 -*-
from django.db.models import Q

from elements.locations.models import EntityLocation
from users.models import CommissionMember, Profile, Role, ROLE_TYPES, WebObserver

# TODO: introduce query generators for other types of counting
def get_roles_query(location):
    if location.date:
        query = Q(location=location)
        if location.is_country():
            query |= Q(location__country=location)
        elif location.is_region():
            query |= Q(location__region=location)
        elif location.is_tik():
            query |= Q(location__tik=location)
    else:
        related = location.related()
        query = Q(location__in=related.values())
        if location.is_country():
            query |= Q(location__country__in=related.values())
        elif location.is_region():
            query |= Q(location__region__in=related.values())
        elif location.is_tik():
            query |= Q(location__tik__in=related.values())

    return query

# TODO: include it in info and cache
# TODO: count members differently?
def get_roles_counters(location):
    counters = {}
    query = get_roles_query(location)

    def filter_inactive_users(queryset):
        return queryset.exclude(profile__user__email='').filter(profile__user__is_active=True)

    roles = list(filter_inactive_users(Role.objects.filter(query)).values_list('type', 'profile'))

    for role_type in ROLE_TYPES:
        counters[role_type] = len(filter(lambda r: r[0]==role_type, roles))

    if location.date:
        related = location.related()
        if None in related:
            no_date_query = get_roles_query(related[None])
            counters['participants'] = EntityLocation.objects.filter(no_date_query).filter(profile__user__is_active=True) \
                    .values_list('profile').distinct().count()
        else:
            counters['participants'] = 0
    else:
        counters['participants'] = EntityLocation.objects.filter(query).filter(profile__user__is_active=True) \
                    .values_list('profile').distinct().count()

    # TODO: use count here?
    #counters['web_observer'] = len(filter_inactive_users(WebObserver.objects.filter(query)) \
    #        .distinct().values_list('user', flat=True))

    counters['commission_members'] = CommissionMember.objects.filter(query).count()

    return counters
