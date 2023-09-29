from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.contrib import messages
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
    """
    For user-only posts on the feed
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        rants = context['rants']
        liked_rants = Like.objects.values('rant').annotate(likes_count=Count('rant'))

        User = get_user_model() 

        for rant in rants:
            rant_uuid = rant.uuid
            if rant_uuid in liked_rants:
                rant.likes_count = liked_rants[rant_uuid]['likes_count']
            else:
                rant.likes_count = 0

            rant.user = User.objects.get(id=rant.user_id)

        return context


class RantDetailView(DetailView):
    model = Rant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rant = context['rant']
        context['rant'] = get_object_or_404(Rant, slug=self.kwargs['slug'])
        context['likes_count'] = rant.likes

        if self.request.user.is_authenticated:
            context['user_like'] = Like.objects.filter(rant=rant, user=self.request.user).exists()
        
        return context


class RantCreateView(LoginRequiredMixin, CreateView):
    model = Rant
    fields = [
        'content',
        'image'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.cleaned_data['image']:
            image = form.cleaned_data['image']
            form.instance.image = image
        return super().form_valid(form)


def like_rant(request, slug):
    rant = get_object_or_404(Rant, slug=slug)


    if not Like.objects.filter(user=request.user, rant=rant).exists():
        Like.objects.create(user=request.user, rant=rant)
        rant.likes += 1
        rant.save()
    return redirect('rants:detail', slug=slug)


def unlike_rant(request, slug):
    rant = get_object_or_404(Rant, slug=slug)
    rant.likes -= 1
    rant.save()

    Like.objects.filter(user=request.user, rant=rant).delete()

    return redirect('rants:detail', slug=slug)