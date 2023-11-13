from django.urls import path

from rantr.conversations.views import conversation_list, conversation_detail, send_message

app_name = 'conversations'

urlpatterns = [
    path('conversations/', conversation_list, name='conversation_list'),
    path('conversation/<str:uuid>/', conversation_detail, name='conversation_detail'),
    path('conversation/<int:user_id>/send/', send_message, name='send_message'),
]