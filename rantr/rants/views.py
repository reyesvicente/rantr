from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)

from rantr.rants.models import Rant, Like


class RantListView(ListView):
    model = Rant
    context_object_name = 'rants'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
    

class RantDetailView(DetailView):
    model = Rant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rant = context['rant']
        context['likes_count'] = rant.likes

        if self.request.user.is_authenticated:
            context['user_like'] = Like.objects.filter(rant=rant, user=self.request.user).exists()
        
        return context


class RantCreateView(LoginRequiredMixin, CreateView):
    model = Rant
    fields = [
        'content'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def like_rant(request, slug):
  rant = get_object_or_404(Rant, slug=slug)
  rant.likes += 1
  rant.save()

  Like.objects.create(user=request.user, rant=rant)

  return redirect('rants:detail', slug=slug)


def unlike_rant(request, slug):
  rant = get_object_or_404(Rant, slug=slug)
  rant.likes -= 1
  rant.save()

  Like.objects.filter(user=request.user, rant=rant).delete()

  return redirect('rants:detail', slug=slug)