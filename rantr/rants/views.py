from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)

from rantr.rants.models import Rant


class RantListView(ListView):
    model = Rant
    context_object_name = 'rants'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
    

class RantDetailView(DetailView):
    model = Rant


class RantCreateView(LoginRequiredMixin, CreateView):
    model = Rant
    fields = [
        'content'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)