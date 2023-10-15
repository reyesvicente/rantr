# from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)

from rantr.rants.models import Rant 
from rantr.likes.models import Like

User = get_user_model()


class RantListView(ListView):

    model = Rant
    context_object_name = 'rants'

    def get_queryset(self):
        return self.model.objects.prefetch_related(
            Prefetch('user', queryset=User.objects.only('id'))  
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        liked_rants = Like.objects.filter(
            user=self.request.user,
            rant__in=context['rants']
        ).values('rant').annotate(likes_count=Count('rant'))
        
        rant_map = {rant.uuid: rant for rant in context['rants']}
        
        for like in liked_rants:
            rant = rant_map[like['rant']]
            rant.user_liked = True
            rant.likes_count = like['likes_count']
            
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


