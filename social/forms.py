from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField


class SignupForm(forms.ModelForm):
    """User creation form compatible with the custom user model.

    Mirrors Django's built-in UserCreationForm but binds to AUTH_USER_MODEL
    explicitly to avoid any swapped-model issues on some setups.
    """

    password1 = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", strip=False, widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ("username",)
        field_classes = {"username": UsernameField}

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
