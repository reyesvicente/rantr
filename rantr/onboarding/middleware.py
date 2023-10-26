from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse


class OnboardingMiddleware(MiddlewareMixin):

  def __call__(self, request):

    if request.user.is_authenticated and not request.user.is_onboarded:

      if request.path != reverse('onboarding:start'):
        return redirect('onboarding:start')

    response = self.get_response(request)  
    return response