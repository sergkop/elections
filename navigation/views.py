# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView

from elections.models import Election
from elements.locations.utils import breadcrumbs_context, subregion_list
from elements.utils import entity_tabs_view
from locations.models import Location
from locations.utils import get_roles_counters, get_roles_query
from locations.views import participants_context
from navigation.forms import FeedbackForm
from services.cache import cache_function

@cache_function('main_page', 30)
def main_page_context():
    total_counter = User.objects.filter(is_active=True).count()

    country = Location.objects.country()
    sub_regions = subregion_list(country)
    return {
        'counters': get_roles_counters(Location.objects.country()),
        'total_counter': total_counter,
    }

class BaseMainView(TemplateView):
    template_name = 'main/base.html'
    tab = ''

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseMainView, self).get_context_data(**kwargs)

        ctx.update(main_page_context())

        self.location = Location.objects.country()

        self.location_query = get_roles_query(self.location)

        self.info = self.location.info(related=True)

        self.tabs = [
            ('main', u'Что делать?', reverse('main'), 'main/view.html'),
            ('wall', u'Комментарии: %i' % self.info['comments']['count'], reverse('wall'), 'locations/wall.html'),
            ('participants', u'Участники', reverse('participants'), 'locations/participants.html'),
            ('elections', u'Выборы', reverse('elections'), 'locations/elections.html'),
        ]

        ctx.update(entity_tabs_view(self))
        ctx.update(breadcrumbs_context(self.location))

        ctx.update({
            'info': self.info,
            'show_date': True,
        })

        #self.data_location = ctx['data_location']

        ctx.update(self.update_context())
        return ctx

class MainView(BaseMainView):
    tab = 'main'
main = MainView.as_view()

class WallView(BaseMainView):
    tab = 'wall'
wall = WallView.as_view()

class ParticipantsView(BaseMainView):
    tab = 'participants'

    def update_context(self):
        return participants_context(self)
country_participants = ParticipantsView.as_view()

class ElectionsView(BaseMainView):
    tab = 'elections'

    def update_context(self):
        return {'elections': Election.objects.all()}
country_elections = ElectionsView.as_view()

def static_page(request, **kwargs):
    """ 
    kwargs must contain the following keys: 'tab', 'template', 'tabs'.
    kwargs['tabs']=[(name, url, template, css_class), ...]
    """
    ctx = breadcrumbs_context(Location.objects.country())
    ctx.update(kwargs)
    return render_to_response(kwargs['template'], context_instance=RequestContext(request, ctx))

def sitemap(request):
    context = {
        'locations': Location.objects.filter(region=None).only('id', 'name'),
    }
    return render_to_response('sitemap.html', context_instance=RequestContext(request, context))

def feedback(request, **kwargs):
    if request.method == 'POST':
        form = FeedbackForm(request, request.POST)
        if form.is_valid():
            form.send()
            return redirect('feedback_thanks')
    else:
        form = FeedbackForm(request)

    ctx = {
        'form': form,
        'template': 'feedback/feedback.html',
    }
    ctx.update(kwargs)
    return static_page(request, **ctx)
