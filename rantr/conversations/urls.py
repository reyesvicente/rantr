from django.urls import path
from rantr.conversations.views import conversation_list, conversation_detail, start_conversation

app_name = 'conversations'

urlpatterns = [
    path('', conversation_list, name='list'),
    path('<int:conversation_id>/', conversation_detail, name='detail'),
    path('start/<str:username>/', start_conversation, name='start'),
]