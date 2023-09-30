from django.urls import path
from .views import RantCreateView, RantDetailView, RantListView

app_name = 'rants'
urlpatterns = [
    path('create/', RantCreateView.as_view(), name='create'),
    path('', RantListView.as_view(), name='list'),
    path('<str:slug>/', RantDetailView.as_view(), name='detail'),
]