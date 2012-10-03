# -*- coding:utf-8 -*-
from random import choice

from django import forms

from crispy_forms.layout import Fieldset, HTML, Layout

from elements.locations.utils import subregion_list
from elements.utils import form_helper
from locations.models import Location
from violations.models import Violation

#@location_init(True, u'Местоположение нарушения')
class ViolationForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = ('type', 'text', 'url')

    helper = form_helper('', u'Сохранить')
    helper.form_id = 'edit_violation_form'

    def save(self, commit=True):
        violation = super(ViolationForm, self).save(commit=False)
        violation.violation_id = choice(range(100000))
        #if commit:
        #    violation.save()
        return violation
