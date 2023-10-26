from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

User = get_user_model()


class OnboardingView(TemplateView):
    template_name = 'onboarding/start.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the currently signed in user
        user = self.request.user

        context['user'] = user
        return context

    def post(self, request):
        # Mark user as onboarded
        request.user.is_onboarded = True 
        request.user.save()
        return redirect('rants:list')
