from django.urls import path

from rantr.users.views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
    follow_user,
    unfollow_user,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
    path('follow/<str:username>', follow_user, name='follow_user'),
    path('unfollow/<str:username>', unfollow_user, name='unfollow_user'),
]