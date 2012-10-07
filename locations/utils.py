# -*- coding:utf-8 -*-
from django.db.models import Q

from users.models import CommissionMember, Profile, Role, ROLE_TYPES, WebObserver

# TODO: introduce query generators for other types of counting
def get_roles_query(location):
    query = Q(location=location)
    if location.is_country():
        query |= Q(location__country=location)
    if location.is_region():
        query |= Q(location__region=location)
    elif location.is_tik():
        query |= Q(location__tik=location)

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

    # TODO: do it for location=None only?
    counters['total'] = Profile.objects.filter(user__is_active=True).count()

    # TODO: use count here?
    #counters['web_observer'] = len(filter_inactive_users(WebObserver.objects.filter(query)) \
    #        .distinct().values_list('user', flat=True))

    counters['commission_members'] = CommissionMember.objects.filter(query).count()

    return counters
