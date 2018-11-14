from django import forms

from . import models


class MessageForm(forms.ModelForm):
    class Meta:
        model = models.Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Message'}),
        }


class SettingsForm(forms.ModelForm):
    class Meta:
        model = models.RoomUser
        fields = ['alert', 'mail_alert']
