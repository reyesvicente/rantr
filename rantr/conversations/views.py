from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from rantr.conversations.models import Conversation
from rantr.conversations.forms import MessageForm

User = get_user_model()


def conversation_list(request):
    conversations = request.user.conversations.all()
    return render(request, 'conversations/conversation_list.html', {'conversations': conversations})


def conversation_detail(request, uuid):
    conversation = get_object_or_404(Conversation, uuid=uuid)
    conversations = conversation.messages.all()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.conversation = conversation
            message.save()
            return redirect('conversations:conversation_detail', uuid=uuid)
    else:
        form = MessageForm()
    return render(request, 'conversations/conversation_detail.html', {'form': form, 'conversation': conversation, 'conversations': conversations})


def send_message(request, user_id):
    sender = request.user
    receiver = get_object_or_404(User, id=user_id)

    # Check if a conversation already exists between the sender and receiver
    conversation = Conversation.objects.filter(participants=sender).filter(participants=receiver).first()

    if not conversation:
        # If not, create a new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(sender, receiver)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.conversation = conversation
            message.save()
            return redirect('conversations:conversation_detail', uuid=conversation.uuid)
    else:
        form = MessageForm()

    return render(request, 'conversations/send_user_message.html', {'form': form, 'receiver': receiver})