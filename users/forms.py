# -*- coding:utf-8 -*-
from django import forms

from crispy_forms.helper import FormHelper

from elements.utils import form_helper
from users.models import CommissionMember, Message, Profile, WebObserver

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)

    helper = form_helper('edit_profile', u'Сохранить')

class MessageForm(forms.ModelForm):
    body = forms.CharField(label=u'Сообщение', widget=forms.Textarea(attrs={'rows': '6'}))

    class Meta:
        model = Message
        fields = ('title', 'body', 'show_email')

class CommissionMemberForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = CommissionMember
        exclude = ('location', 'user', 'time')

class WebObserverForm(forms.ModelForm):
    start_time = forms.IntegerField(u'Начало наблюдения', widget=forms.Select(choices=[(i, str(i)+'.00') for i in range(7, 24)]))
    end_time = forms.IntegerField(u'Окончание наблюдения', widget=forms.Select(choices=[(i, str(i)+'.00') for i in range(8, 24)]+[(24, '0.00')]))

    class Meta:
        model = WebObserver
        exclude = ('location', 'user', 'time', 'capture_video')
