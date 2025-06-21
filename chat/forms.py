from django import forms
from .models import ChatMessage

class ChatMessageForm(forms.ModelForm):
    """
    Form for sending a new chat message.
    It includes a single field for the message content.
    """
    class Meta:
        model = ChatMessage
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Type your message...',
                'class': 'form-control',
                'autocomplete': 'off'
            }),
        }
        labels = {
            'content': '',  # No label needed for the chat input field
        }
