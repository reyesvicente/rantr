from django.urls import path
from .views import like_rant, unlike_rant, RantCreateView, RantDetailView, RantListView

app_name = 'rants'
urlpatterns = [
    path('create/', RantCreateView.as_view(), name='create'),
    path('', RantListView.as_view(), name='list'),
    path('<str:slug>/', RantDetailView.as_view(), name='detail'),
    path('rant/<str:slug>/like/', like_rant, name='rant-like'),
    path('rant/<str:slug>/unlike/', unlike_rant, name='rant-unlike'),
]