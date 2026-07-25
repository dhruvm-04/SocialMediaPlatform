from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Comment, Post


class SignupForm(UserCreationForm):
	"""Registration form built on Django's built-in UserCreationForm."""

	class Meta:
		model = User
		fields = ("username", "email")


class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ("content",)
		widgets = {"content": forms.Textarea(attrs={"rows": 4, "placeholder": "Share something..."})}


class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ("content",)
		widgets = {"content": forms.TextInput(attrs={"placeholder": "Add a comment"})}