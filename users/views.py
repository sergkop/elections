# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from grakon.utils import authenticated_ajax_post, escape_html
from elements.participants.models import participant_in
from elements.utils import table_data
from elements.views import entity_base_view, entity_tabs_view
from services.email import send_email
from users.forms import MessageForm, ProfileForm
from users.models import Message, Profile

class BaseProfileView(object):
    template_name = 'profiles/base.html'
    tab = None # 'view' or 'edit'

    def update_context(self):
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(BaseProfileView, self).get_context_data(**kwargs)

        if self.tab == 'view':
            user_id = int(self.kwargs.get('id'))
        else:
            user_id = self.request.profile.user_id

        ctx.update(entity_base_view(self, Profile, {'user': user_id}))

        self.own_profile = (self.entity==self.request.profile)

        if self.own_profile:
            self.tabs = [
                ('view', u'Инфо', reverse('profile', args=[user_id]), 'profiles/view.html'),
                ('edit', u'Редактировать', reverse('edit_profile'), 'profiles/edit.html'),
            ]
        else:
            self.tabs = []

        ctx.update(entity_tabs_view(self))

        if len(ctx['info']['locations']['entities']) > 0:
            location = ctx['info']['locations']['entities'][0]['instance']
        else:
            location = None

        ctx.update({
            'title': unicode(self.entity),
            'profile': self.entity,
            'is_admin': self.own_profile,
            'location': location,

            'message_form': MessageForm(),
        })
        ctx.update(self.update_context())
        return ctx

class ProfileView(BaseProfileView, TemplateView):
    tab = 'view'

class EditProfileView(BaseProfileView, UpdateView):
    tab = 'edit'
    form_class = ProfileForm

    def get_user(self):
        return self.request.user

    def get_object(self):
        return self.request.profile

    def get_success_url(self):
        return reverse('my_profile')

edit_profile = login_required(EditProfileView.as_view())

def remove_account(request):
    if request.user.is_authenticated():
        # TODO: fix the way to send user notification of account deletion
        subject = u'[УДАЛЕНИЕ АККАУНТА] id=%s - %s %s' % (request.user.id,
                request.profile.first_name, request.profile.last_name)
        send_email(None, subject, 'letters/remove_account.html', {'profile': request.profile},
                'remove_account', 'noreply')
        return HttpResponse('ok')
    return HttpResponse(u'Чтобы удалить аккаунт, необходимо войти в систему')

@login_required
def profile(request):
    """ Redirects user to profile page after logging in (used to overcome django limitation) """
    return redirect(request.profile.get_absolute_url())

# TODO: limit the number of messages User can send daily (also depends on his points)
@authenticated_ajax_post
def send_message(request):
    form = MessageForm(request.POST)

    # TODO: what happens if title in post data is longer than model field max_length?
    if not form.is_valid():
        # TODO: show error messages u'Необходимо указать тему письма', u'Сообщение не должно быть пустым'
        return HttpResponse('Форма заполнена неверно')

    try:
        recipient_id = int(request.POST.get('id', ''))
        recipient = Profile.objects.select_related('user').get(id=recipient_id)
    except ValueError, Profile.DoesNotExist:
        return HttpResponse(u'Получатель указан неверно')

    title = escape_html(form.cleaned_data['title'])
    body = escape_html(form.cleaned_data['body'])
    show_email = form.cleaned_data['show_email']

    subject = u'Пользователь %s написал вам сообщение' % unicode(request.profile)
    ctx = {
        'title': title,
        'body': body,
        'show_email': show_email,
        'sender': request.profile,
    }
    send_email(recipient, subject, 'letters/message.html', ctx, 'message', 'noreply',
            reply_to=request.profile.user.email if show_email else None)

    Message.objects.create(sender=request.profile, receiver=recipient, title=title,
            body=body, show_email=show_email)

    return HttpResponse('ok')
