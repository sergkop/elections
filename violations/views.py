# -*- coding:utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from users.models import Profile
from violations.forms import ViolationForm
from violations.models import Violation

class ViolationView(DetailView):
    template_name = 'violations/view.html'
    model = Violation
    slug = 'id'

    def get_object(self, queryset=None):
        try:
            violation_id = int(self.kwargs.get('violation_id', ''))
        except ValueError:
            raise Http404(u'Неправильно указан идентификатор нарушения')

        return get_object_or_404(Violation.objects.select_related(), id=violation_id)

    def get_context_data(self, **kwargs):
        ctx = super(ViolationView, self).get_context_data(**kwargs)

        ctx.update({
            'violation': self.object,
            'violation_id': self.kwargs['violation_id'],
        })
        return ctx

violation_view = ViolationView.as_view()

class ReportViolationView(CreateView):
    template_name = 'violations/create.html'
    form_class = ViolationForm
    model = Violation

    def form_valid(self, form):
        violation = form.save(commit=False)
        violation.source = self.request.profile
        violation.save()

        response = super(ReportViolationView, self).form_valid(form)
        return response

report_violation = login_required(ReportViolationView.as_view())
