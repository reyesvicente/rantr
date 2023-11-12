from django import forms
from rantr.messaging.models import DirectMessage


class MessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content']