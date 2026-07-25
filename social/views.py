from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm, SignupForm
from .models import Comment, Friendship, Post


def register(request):
	if request.method == "POST":
		form = SignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Welcome! Your account has been created.")
			return redirect("home")
	else:
		form = SignupForm()
	return render(request, "register.html", {"form": form})


def home(request):
	"""Global feed: every post, newest first."""
	posts = Post.objects.select_related("user").order_by("-created_at")
	return render(request, "home.html", {"posts": posts, "post_form": PostForm(), "comment_form": CommentForm()})


@login_required
def profile(request, username):
	profile_user = get_object_or_404(User, username=username)
	posts = Post.objects.filter(user=profile_user).select_related("user").order_by("-created_at")
	is_friend = profile_user != request.user and Friendship.are_friends(request.user, profile_user)
	friends = Friendship.friends_of(profile_user)
	return render(request, "profile.html", {
		"profile_user": profile_user,
		"posts": posts,
		"is_friend": is_friend,
		"friends": friends,
	})


@login_required
def post_create(request):
	if request.method == "POST":
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.user = request.user
			post.save()
			messages.success(request, "Post created.")
			return redirect("home")
	else:
		form = PostForm()
	return render(request, "post_form.html", {"form": form})


@login_required
def post_edit(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	if post.user != request.user:
		return HttpResponseForbidden("You cannot edit this post.")
	if request.method == "POST":
		form = PostForm(request.POST, instance=post)
		if form.is_valid():
			form.save()
			messages.success(request, "Post updated.")
			return redirect("home")
	else:
		form = PostForm(instance=post)
	return render(request, "post_form.html", {"form": form, "post": post})


@login_required
def post_delete(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	if post.user != request.user:
		return HttpResponseForbidden("You cannot delete this post.")
	if request.method == "POST":
		post.delete()
		messages.success(request, "Post deleted.")
	return redirect("home")


@login_required
def post_like_toggle(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	if request.user in post.likes.all():
		post.likes.remove(request.user)
	else:
		post.likes.add(request.user)
	return redirect(request.META.get("HTTP_REFERER") or reverse("home"))


@login_required
def comment_add(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	form = CommentForm(request.POST)
	if form.is_valid():
		comment = form.save(commit=False)
		comment.post = post
		comment.user = request.user
		comment.save()
	else:
		messages.error(request, "Comment cannot be empty.")
	return redirect(request.META.get("HTTP_REFERER") or reverse("home"))


@login_required
def friend_add(request, username):
	target = get_object_or_404(User, username=username)
	if target == request.user:
		messages.error(request, "You cannot friend yourself.")
	else:
		lo, hi = sorted([request.user.id, target.id])
		Friendship.objects.get_or_create(user1_id=lo, user2_id=hi)
		messages.success(request, f"You are now friends with {target.username}.")
	return redirect("profile", username=username)


@login_required
def friend_remove(request, username):
	target = get_object_or_404(User, username=username)
	lo, hi = sorted([request.user.id, target.id])
	Friendship.objects.filter(user1_id=lo, user2_id=hi).delete()
	messages.success(request, f"Removed {target.username} from your friends.")
	return redirect("profile", username=username)