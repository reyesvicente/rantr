from django.urls import path
from rantr.profiles.views import dashboard, profile_list, profile

app_name = 'profiles'
urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('profile-list/', profile_list, name='profile_list'),
    path('profile/<str:uuid>/', profile, name='profile')
]