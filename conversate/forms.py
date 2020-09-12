from django import forms

from . import models


class MessageForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = models.Message
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'placeholder': 'Message',
                    'rows': 1,
                },
            ),
        }


class SettingsForm(forms.ModelForm):
    class Meta:
        model = models.RoomUser
        fields = ['alert', 'mail_alert']
