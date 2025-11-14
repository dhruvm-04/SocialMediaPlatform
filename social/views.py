from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Comment, Friendship, Like, Post, Profile
from .forms import SignupForm


def register(request):
	if request.method == 'POST':
		# Use custom form bound to AUTH_USER_MODEL to avoid swapped-model issues
		form = SignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			# Create a profile automatically
			Profile.objects.get_or_create(user=user)
			messages.success(request, 'Registration successful. You can now log in.')
			return redirect('login')
	else:
		form = SignupForm()
	return render(request, 'register.html', {'form': form})


def signup(request):
	"""Alternate route for user registration to ensure the custom form is used."""
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			Profile.objects.get_or_create(user=user)
			messages.success(request, 'Registration successful. You can now log in.')
			return redirect('login')
	else:
		form = SignupForm()
	return render(request, 'register.html', {'form': form})


def home(request):
	"""
	Homepage feed.
	- If user is authenticated: show friends + self posts; if empty, fall back to global feed.
	- If anonymous: show global feed so that posts are visible without login.
	"""
	empty_feed = False

	if request.user.is_authenticated:
		# Build friend list (accepted friendships) + self
		User = get_user_model()
		friends_qs = User.objects.filter(
			friendships_initiated__user2=request.user, friendships_initiated__status='accepted'
		).union(
			User.objects.filter(friendships_received__user1=request.user, friendships_received__status='accepted')
		)
		friend_ids = list(friends_qs.values_list('id', flat=True)) + [request.user.id]
		posts = (
			Post.objects.filter(user_id__in=friend_ids)
			.select_related('user')
			.prefetch_related('comments__user', 'likes')
		)
		if not posts.exists():
			# No friend posts yet – show global feed
			posts = (
				Post.objects.all()
				.select_related('user')
				.prefetch_related('comments__user', 'likes')[:50]
			)
			empty_feed = True
	else:
		# Anonymous visitors see global feed (read-only)
		posts = (
			Post.objects.all()
			.select_related('user')
			.prefetch_related('comments__user', 'likes')[:50]
		)

	return render(request, 'home.html', {'posts': posts, 'empty_feed': empty_feed})


@login_required
def profile(request, username):
	User = get_user_model()
	profile_user = get_object_or_404(User, username=username)
	posts = (
		Post.objects.filter(user=profile_user)
		.select_related('user')
		.prefetch_related('comments__user', 'likes')
	)
	# Determine friendship status
	u1, u2 = sorted([request.user.id, profile_user.id])
	friendship = Friendship.objects.filter(user1_id=u1, user2_id=u2).first()
	# Aggregate stats
	friends = list(Friendship.friends_of(profile_user))
	likes_given = profile_user.likes.count()
	comments_made = profile_user.comments.count()
	return render(request, 'profile.html', {
		'profile_user': profile_user,
		'posts': posts,
		'friendship': friendship,
		'friends': friends,
		'likes_given': likes_given,
		'comments_made': comments_made,
	})


@login_required
def post_create(request):
	if request.method == 'POST':
		content = request.POST.get('content', '').strip()
		if content:
			Post.objects.create(user=request.user, content=content)
			messages.success(request, 'Post created.')
			return redirect('home')
		messages.error(request, 'Content cannot be empty.')
	return render(request, 'post_form.html')


@login_required
def post_edit(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	if post.user != request.user:
		return HttpResponseForbidden('You cannot edit this post.')
	if request.method == 'POST':
		content = request.POST.get('content', '').strip()
		if content:
			post.content = content
			post.save()
			messages.success(request, 'Post updated.')
			return redirect('home')
		messages.error(request, 'Content cannot be empty.')
	return render(request, 'post_form.html', {'post': post})


@login_required
def post_delete(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	if post.user != request.user:
		return HttpResponseForbidden('You cannot delete this post.')
	if request.method == 'POST':
		post.delete()
		messages.success(request, 'Post deleted.')
		return redirect('home')
	return render(request, 'confirm_delete.html', {'object': post, 'type': 'post'})


@login_required
def post_like_toggle(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	like, created = Like.objects.get_or_create(user=request.user, post=post)
	if not created:
		like.delete()
		messages.info(request, 'Unliked the post.')
	else:
		messages.success(request, 'Liked the post.')
	return redirect(request.META.get('HTTP_REFERER') or reverse('home'))


@login_required
def comment_add(request, post_id):
	post = get_object_or_404(Post, id=post_id)
	content = request.POST.get('content', '').strip()
	if content:
		Comment.objects.create(user=request.user, post=post, content=content)
		messages.success(request, 'Comment added.')
	else:
		messages.error(request, 'Comment cannot be empty.')
	return redirect(request.META.get('HTTP_REFERER') or reverse('home'))


@login_required
def comment_delete(request, comment_id):
	comment = get_object_or_404(Comment, id=comment_id)
	if comment.user != request.user and comment.post.user != request.user:
		return HttpResponseForbidden('You cannot delete this comment.')
	if request.method == 'POST':
		comment.delete()
		messages.success(request, 'Comment deleted.')
	return redirect(request.META.get('HTTP_REFERER') or reverse('home'))


@login_required
def friend_request(request, username):
	User = get_user_model()
	target = get_object_or_404(User, username=username)
	if target == request.user:
		messages.error(request, 'You cannot friend yourself.')
		return redirect('profile', username=username)
	u1, u2 = sorted([request.user.id, target.id])
	friendship, created = Friendship.objects.get_or_create(user1_id=u1, user2_id=u2)
	if created:
		# If requester is the higher id user, status pending still makes sense
		messages.success(request, 'Friend request sent.')
	else:
		if friendship.status == 'accepted':
			messages.info(request, 'You are already friends.')
		elif friendship.status == 'pending':
			messages.info(request, 'Friend request is already pending.')
		else:
			messages.info(request, f'Current status: {friendship.status}.')
	return redirect('profile', username=username)


@login_required
def friend_accept(request, friendship_id):
	friendship = get_object_or_404(Friendship, id=friendship_id)
	# Only the other user can accept
	if request.user.id not in [friendship.user1_id, friendship.user2_id]:
		return HttpResponseForbidden('Not your friendship request.')
	if friendship.status != 'accepted':
		friendship.status = 'accepted'
		friendship.save()
		messages.success(request, 'Friend request accepted.')
	return redirect(request.META.get('HTTP_REFERER') or reverse('home'))

