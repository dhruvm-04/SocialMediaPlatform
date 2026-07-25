from django.contrib.auth.models import User
from django.db import models


class Friendship(models.Model):
	"""An established (already-mutual) friendship between two users.

	No request/accept workflow: adding a friendship immediately makes the
	two users friends. Stored once per pair, with user1_id < user2_id, so
	the reverse pair is never duplicated.
	"""

	user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendships_as_user1")
	user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friendships_as_user2")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.CheckConstraint(condition=~models.Q(user1=models.F("user2")), name="friendship_no_self"),
			models.UniqueConstraint(fields=["user1", "user2"], name="unique_friendship_pair"),
		]

	def save(self, *args, **kwargs):
		# Keep a consistent (lower_id, higher_id) ordering so (A, B) and (B, A)
		# are always stored as the same row.
		if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
			self.user1_id, self.user2_id = self.user2_id, self.user1_id
		super().save(*args, **kwargs)

	def __str__(self):
		return f"Friendship({self.user1.username}, {self.user2.username})"

	@staticmethod
	def are_friends(user_a, user_b):
		lo, hi = sorted([user_a.id, user_b.id])
		return Friendship.objects.filter(user1_id=lo, user2_id=hi).exists()

	@staticmethod
	def friends_of(user):
		friend_ids = list(
			Friendship.objects.filter(user1=user).values_list("user2_id", flat=True)
		) + list(
			Friendship.objects.filter(user2=user).values_list("user1_id", flat=True)
		)
		return User.objects.filter(id__in=friend_ids)


class Post(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Post({self.id}) by {self.user.username}"


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["created_at"]

	def __str__(self):
		return f"Comment({self.id}) by {self.user.username} on Post {self.post_id}"