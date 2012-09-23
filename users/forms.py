# -*- coding:utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from elements.utils import form_helper
from users.models import CommissionMember, Message, WebObserver

class MessageForm(forms.ModelForm):
    body = forms.CharField(label=u'Сообщение', widget=forms.Textarea(attrs={'rows': '6'}))

    class Meta:
        model = Message
        fields = ('title', 'body', 'show_email')

class FeedbackForm(forms.Form):
    name = forms.CharField(label=u'Ваше имя')
    email = forms.CharField(label=u'Электронная почта')
    body = forms.CharField(widget=forms.Textarea(attrs={'style': 'width:100%;'}), label=u'Сообщение')

    helper = form_helper('feedback', u'Отправить')

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(FeedbackForm, self).__init__(*args, **kwargs)
        if self.request.user.is_authenticated():
            del self.fields['name']
            del self.fields['email']

    def send(self):
        ctx = {
            'message': self.cleaned_data['body'],
            'user': self.request.user,
        }
        ctx['name'] = self.cleaned_data.get('name', '')
        ctx['email'] = self.cleaned_data.get('email', '')
        if self.request.user.is_authenticated():
            ctx['link']  = u'%s%s' % (settings.URL_PREFIX, reverse(
                    'profile', kwargs={'username': self.request.user.username}))
        from_mail = settings.DEFAULT_FROM_EMAIL
        message = render_to_string('feedback/mail.txt', ctx)
        
        # TODO: send mail using Amazon SES
        send_mail(u'[ОБРАТНАЯ СВЯЗЬ]', message, from_mail, [from_mail], fail_silently=False)

class CommissionMemberForm(forms.ModelForm):
    class Meta:
        model = CommissionMember
        exclude = ('location', 'user', 'time')

class WebObserverForm(forms.ModelForm):
    start_time = forms.IntegerField(u'Начало наблюдения', widget=forms.Select(choices=[(i, str(i)+'.00') for i in range(7, 24)]))
    end_time = forms.IntegerField(u'Окончание наблюдения', widget=forms.Select(choices=[(i, str(i)+'.00') for i in range(8, 24)]+[(24, '0.00')]))

    class Meta:
        model = WebObserver
        exclude = ('location', 'user', 'time', 'capture_video')
