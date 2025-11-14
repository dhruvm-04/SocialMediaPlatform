from django.conf import settings
from django.db import models
from django.db.models import Q, F
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
class User(AbstractUser):
	GENDER_CHOICES = [
		("M", "Male"),
		("F", "Female"),
		("O", "Other"),
	]
	dob = models.DateField(null=True, blank=True)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

	class Meta:
		db_table = 'social_user'
		ordering = ['username']

	def __str__(self):
		return f"User({self.username})"



class Profile(models.Model):
	# Keeping profile for future extension (avatars, bio) even though dob/gender moved to User
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
	bio = models.CharField(max_length=160, blank=True)

	def __str__(self):
		return f"Profile({self.user.username})"


class Post(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Post({self.id}) by {self.user.username}"


class Friendship(models.Model):
	STATUS_CHOICES = [
		("pending", "Pending"),
		("accepted", "Accepted"),
		("declined", "Declined"),
		("blocked", "Blocked"),
	]

	user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friendships_initiated")
	user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friendships_received")
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.CheckConstraint(check=~models.Q(user1=F("user2")), name="friendship_no_self"),
			models.UniqueConstraint(fields=["user1", "user2"], name="unique_friendship_pair"),
		]

	def save(self, *args, **kwargs):
		# Ensure (user1.id < user2.id) ordering to avoid duplicates in reverse order
		if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
			self.user1_id, self.user2_id = self.user2_id, self.user1_id
		super().save(*args, **kwargs)

	def __str__(self):
		return f"Friendship({self.user1.username}, {self.user2.username}) [{self.status}]"

	@staticmethod
	def friends_of(user):
		User = get_user_model()
		return User.objects.filter(
			Q(friendships_initiated__user2=user, friendships_initiated__status="accepted") |
			Q(friendships_received__user1=user, friendships_received__status="accepted")
		).distinct()


class Like(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("user", "post")

	def __str__(self):
		return f"Like({self.user.username} -> Post {self.post_id})"


class Comment(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["created_at"]

	def __str__(self):
		return f"Comment({self.id}) by {self.user.username} on Post {self.post_id}"


class Notification(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
	message = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField(default=False)

	def __str__(self):
		return f"Notification({self.id}) to {self.user.username}"

