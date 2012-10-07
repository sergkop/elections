# -*- coding:utf-8 -*-
from django.shortcuts import get_object_or_404

from elements.participants.models import EntityParticipant

# TODO: if there is a single location - add to ctx (admin as well?)
def entity_base_view(view, entity_model, selector):
    """ selector is a dict uniquely identifying the entity """
    view.entity = get_object_or_404(entity_model, **selector)
    view.info = view.entity.info()

    ctx = {'info': view.info}

    # TODO: all data can be recieved in one db query
    for role in entity_model.roles:
        if view.request.user.is_authenticated():
            ctx['is_'+role] = EntityParticipant.objects.is_participant(view.entity, view.request.profile, role)
        else:
            ctx['is_'+role] = False

    ctx.update(view.update_context())
    return ctx

def entity_tabs_view(view):
    return {
        'tab': view.tab,
        'tabs': view.tabs,
        'template_path': filter(lambda t: t[0]==view.tab, view.tabs)[0][3] if view.tabs else '',
    }
