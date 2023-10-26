from django.urls import path

from rantr.onboarding.views import OnboardingView

app_name = 'onboarding'
urlpatterns = [
    path('start/', OnboardingView.as_view(), name='start'),
]