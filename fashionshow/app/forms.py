from django import forms
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

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
