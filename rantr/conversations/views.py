from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rantr.conversations.models import Conversation, Message
from rantr.users.models import User
from rantr.notifications.models import Notification


@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(
        Q(initiator=request.user) | Q(receiver=request.user)
    ).order_by('-updated_at')
    
    context = {'conversations': conversations}
    return render(request, 'conversations/conversation_list.html', context)


@login_required
def conversation_detail(request, conversation_id):
    # First filter by conversation ID
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Then check if user has access
    if not (conversation.initiator == request.user or conversation.receiver == request.user):
        return redirect('conversations:list')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Determine the recipient (the other user in the conversation)
            recipient = conversation.receiver if conversation.initiator == request.user else conversation.initiator
            
            # Create notification for the message
            Notification.objects.create(
                recipient=recipient,
                actor=request.user,
                verb='messaged',
                target_content_type=ContentType.objects.get_for_model(conversation),
                target_object_id=conversation.id,
                description=f"{request.user.username} sent you a message"
            )
            
            conversation.save()  # Updates the updated_at timestamp
    
    messages = conversation.messages.order_by('created_at')
    context = {
        'conversation': conversation,
        'messages': messages
    }
    return render(request, 'conversations/conversation_detail.html', context)


@login_required
def start_conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    
    if other_user == request.user:
        return redirect('conversations:list')
    
    # Check if a conversation already exists
    conversation = Conversation.objects.filter(
        (Q(initiator=request.user) & Q(receiver=other_user)) |
        (Q(initiator=other_user) & Q(receiver=request.user))
    ).first()
    
    if conversation:
        return redirect('conversations:detail', conversation_id=conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create(
        initiator=request.user,
        receiver=other_user
    )
    
    # Create notification for the receiver
    Notification.objects.create(
        recipient=other_user,
        actor=request.user,
        verb='started conversation',
        target_content_type=ContentType.objects.get_for_model(conversation),
        target_object_id=conversation.id,
        description=f"{request.user.username} started a conversation with you"
    )
    
    return redirect('conversations:detail', conversation_id=conversation.id)