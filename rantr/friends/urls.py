from django.urls import path

from rantr.friends.views import follow_user, unfollow_user

app_name = 'friends'
urlpatterns = [
    path('<str:username>/follow/', follow_user, name='follow'), 
    path('<str:username>/unfollow/', unfollow_user, name='unfollow'),
]