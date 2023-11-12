from django.urls import path

from rantr.messaging.views import ConversationListView, ConversationDetailView, SendMessageView

app_name = 'messaging'
urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('send-message/<str:username>/', SendMessageView.as_view(), name='send_message'),
]