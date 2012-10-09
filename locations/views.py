# -*- coding:utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView

from elections.models import Election, ElectionLocation
from elements.locations.models import EntityLocation
from elements.locations.utils import breadcrumbs_context, subregion_list
from elements.utils import entity_tabs_view
from locations.models import Location
from locations.utils import get_roles_counters, get_roles_query
from users.forms import CommissionMemberForm, WebObserverForm
from users.models import CommissionMember, Profile, Role, ROLE_CHOICES, ROLE_TYPES, WebObserver
from violations.models import Violation

# TODO: web_observers tab is not activated for tiks and lead to crush
class BaseLocationView(TemplateView):
    template_name = 'locations/base.html'
    tab = ''

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseLocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        try:
            self.location = location = Location.objects.select_related().get(id=loc_id)
        except Location.DoesNotExist:
            raise Http404(u'Избирательный округ не найден')

        # TODO: different query generators might be needed for different data types
        self.location_query = get_roles_query(location)

        self.info = location.info(related=True)

        self.tabs = [
            ('wall', u'Комментарии: %i' % self.info['comments']['count'], reverse('location_wall', args=[location.id]), 'locations/wall.html'),
            ('participants', u'Участники', reverse('location_participants', args=[location.id]), 'locations/participants.html'),
            ('info', u'Информация', reverse('location_info', args=[location.id]), 'locations/info.html'),
            ('elections', u'Выборы', reverse('location_elections', args=[location.id]), 'locations/elections.html'),
            ('violations', u'Нарушения', reverse('location_violations', args=[location.id]), 'locations/violations.html'),
        ]

        ctx.update(entity_tabs_view(self))
        ctx.update(breadcrumbs_context(location))

        self.data_location = ctx['data_location']

        ctx.update({
            'loc_id': kwargs['loc_id'],

            'info': self.info,
            'show_date': True,

            'counters': get_roles_counters(location),

            'add_commission_member_form': CommissionMemberForm(),
            'become_web_observer_form': WebObserverForm(),

            'ROLE_CHOICES': ROLE_CHOICES,
        })

        ctx.update(self.update_context())
        return ctx

class InfoView(BaseLocationView):
    tab = 'info'

    def update_context(self):
        return {'commission_members': CommissionMember.objects.filter(location=self.data_location)}

class WallView(BaseLocationView):
    tab = 'wall'

    def update_context(self):
        return {}

class ViolationsView(BaseLocationView):
    tab = 'violations'

    def update_context(self):
        if self.location.date is None:
            return {}
        else:
            query = Q(location=self.location)

            if self.location.is_country:
                query = Q(location=self.location)
            else:
                query = Q(location=self.location)
                if location.is_region():
                    query |= Q(location__region=self.location)
                elif location.is_tik():
                    query |= Q(location__tik=self.location)

            return {
                'violations': Violation.objects.filter(query)[:100],
            }

class ElectionsView(BaseLocationView):
    tab = 'elections'

    def update_context(self):
        election_ids = list(ElectionLocation.objects.filter(self.location_query).distinct().values_list('election', flat=True))
        return {'elections': Election.objects.filter(id__in=election_ids)}

def participants_context(view):
    role_type = view.request.GET.get('type', '')
    if not role_type in ROLE_TYPES:
        role_type = ''

    # TODO: use pagination
    if role_type == '':
        profile_ids = EntityLocation.objects.filter(view.location_query).values_list('entity_id', flat=True)[:100]
        profiles = Profile.objects.filter(id__in=profile_ids, user__is_active=True)
    else:
        roles = Role.objects.filter(view.location_query).filter(type=role_type).select_related('profile')[:100]
        profiles = sorted(set(role.profile for role in roles), key=lambda profile: unicode(profile))

    return {
        'participants': profiles,
        'selected_role_type': role_type,
    }

class ParticipantsView(BaseLocationView):
    tab = 'participants'

    def update_context(self):
        return participants_context(self)

class LinksView(BaseLocationView):
    tab = 'links'

    def update_context(self):
        return {
            'view': 'locations/links.html',
            'links': list(Link.objects.filter(location=self.location)),
        }

class WebObserversView(BaseLocationView):
    def update_context(self):
        web_observers = WebObserver.objects.filter(location=self.location).select_related('user__user')
        web_observers_by_time = {}
        for web_observer in web_observers:
            for time in range(web_observer.start_time, web_observer.end_time):
                web_observers_by_time.setdefault(time, []).append(web_observer)

        times = []
        for time in range(7, 24):
            times.append({'start_time': time, 'web_observers': web_observers_by_time.get(time, [])})
            times[-1]['end_time'] = time+1 if time<23 else 0

        return {
            'view': 'locations/web_observers.html',
            'times': times,
        }

def get_subregions(request):
    if not request.is_ajax():
        return HttpResponse('[]')

    loc_id = request.GET.get('loc_id', '')

    if loc_id:
        try:
            location = Location.objects.get(id=int(loc_id))
        except ValueError, Location.DoesNotExist:
            return HttpResponse('[]')
    else:
        location = None

    return HttpResponse(json.dumps(subregion_list(location), ensure_ascii=False))

# TODO: restructure it and take only one parameter
def goto_location(request):
    tab = request.GET.get('tab', '')
    for name in ('uik', 'tik', 'region'):
        try:
            location_id = int(request.GET.get(name, ''))
        except ValueError:
            continue

        url = reverse('location_info', args=[location_id])
        if tab:
            url += '/' + tab
        return HttpResponseRedirect(url)

    return HttpResponseRedirect(reverse('main'))

def add_commission_member(request):
    if request.method=='POST' and request.is_ajax() and request.user.is_authenticated():
        try:
            location_id = int(request.POST.get('location'))
        except ValueError:
            return HttpResponse(u'Неверно указан избирательный округ')

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return HttpResponse(u'Неверно указан избирательный округ')

        form = CommissionMemberForm(request.POST)
        if form.is_valid():
            commission_member = form.save(commit=False)
            commission_member.location = location
            commission_member.user = request.profile
            commission_member.save()
            return HttpResponse('ok')
        else:
            return HttpResponse(u'Заполните обязательные поля')

    return HttpResponse(u'Ошибка')
