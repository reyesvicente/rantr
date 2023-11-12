from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.views import View
from django.views.generic import ListView, FormView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from notifications.signals import notify

from rantr.messaging.models import Message, Conversation
from rantr.messaging.forms import MessageForm

User = get_user_model()


class ConversationListView(LoginRequiredMixin, ListView):
    model = Message
    context_object_name = 'messages'
    template_name = "messaging/conversation_list.html"

    def get_queryset(self):
        return self.request.user.conversations.prefetch_related('messages').all()


class ConversationDetailView(LoginRequiredMixin, FormView, DetailView):
    model = Conversation
    template_name = 'messaging/conversation_detail.html'
    context_object_name = 'conversation'
    form_class = MessageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['messages'] = self.object.messages.all()
            context['form'] = MessageForm(self.request.POST or None)
        else:
            # Handle the case where the conversation is not found
            context['messages'] = []
            context['form'] = MessageForm()

        return context

    def get_object(self, queryset=None):
        # Ensure you are correctly fetching the conversation based on the URL parameter
        conversation_id = self.kwargs.get('pk')
        if conversation_id is not None:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            if self.request.user in conversation.participants.all():
                return conversation
            else:
                print("User is not a participant in the conversation.")
        else:
            print("Conversation ID is not present.")

        return None  # Return None if conversation_id is not present or user is not a participant
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.conversation = self.object
            new_message.sender = self.request.user
            new_message.save()
            # Notify the other participants in the conversation
            participants = self.object.participants.exclude(id=self.request.user.id)
            for participant in participants:
                notify.send(
                    sender=request.user,
                    recipient=participant,
                    verb='New message received',
                    description=f'You have a new message from {request.user.username} in the conversation {self.object}',
                    target=self.object,
                )
            form = self.get_form()  # Reset the form after sending a message
        
        context = self.get_context_data()
        return self.render_to_response(context)


class SendMessageView(View):
    template_name = 'messaging/send_message.html'
    form_class = MessageForm

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        form = self.form_class()
        return render(request, self.template_name, {'user': user, 'form': form})

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        form = self.form_class(request.POST)

        if form.is_valid():
            # Get or create a conversation based on participants' IDs
            user_ids = [request.user.id, user.id]
            conversation = Conversation.objects.get_or_create_participants(*user_ids)

            new_message = form.save(commit=False)
            new_message.conversation = conversation
            new_message.sender = request.user
            new_message.save()

            # Notify the recipient
            notify.send(
                sender=request.user,
                recipient=user,
                verb='New message received',
                description=f'You have a new message from {request.user.username}',
                target=new_message,
            )

            return redirect('messaging:conversation_list')

        return render(request, self.template_name, {'user': user, 'form': form})