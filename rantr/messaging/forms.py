from django import forms
from rantr.messaging.models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']