from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your Name',
                'required': True,
                'maxlength': '120',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Your Message',
                'required': True,
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Please provide your name.')
        return name

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise forms.ValidationError('Please write a message.')
        return message
