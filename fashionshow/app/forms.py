from django import forms
from .models import CustomUser, Comment
from django.utils.translation import gettext_lazy as _

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'message']

    # Валидация поля "Тема комментария"
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if not subject:
            raise forms.ValidationError(_('Тема комментария не может быть пустой.'))
        if len(subject) > 255:
            raise forms.ValidationError(_('Тема комментария не может быть длиннее 255 символов.'))
        return subject

    # Валидация поля "Сообщение"
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message or message.strip() == '':
            raise forms.ValidationError(_('Сообщение не может быть пустым.'))
        if len(message) > 1000:
            raise forms.ValidationError(_('Сообщение не может быть длиннее 1000 символов.'))
        return message


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ["email", "password"]

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            raise forms.ValidationError(_("Password is required."))
        return password
