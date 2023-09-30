from django.urls import path
from .views import like_rant, unlike_rant

app_name = 'likes'
urlpatterns = [
    path('<str:slug>/like/', like_rant, name='rant-like'),
    path('<str:slug>/unlike/', unlike_rant, name='rant-unlike'),
]