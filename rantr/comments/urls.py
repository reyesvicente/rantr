from django.urls import path

from rantr.comments.views import add_comment

app_name = 'comments'
urlpatterns = [
    path('rant/<str:rant_uuid>/comment/', add_comment, name='add_comment'),
]