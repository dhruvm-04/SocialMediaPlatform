import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from social.models import Comment, Friendship, Post

USERNAMES = ["aarav", "ishita", "rohan", "priya", "kavya", "dhruv"]
PASSWORD = "Password@123"

POST_SAMPLES = [
	"Just had chai with friends.",
	"Exploring Bengaluru traffic today.",
	"Weekend getaway to Coorg was great.",
	"Coding late night, need more coffee.",
	"Campus placements season is stressful!",
	"Watched a great movie last night.",
]

COMMENT_SAMPLES = ["Nice post!", "Agreed!", "Interesting.", "Haha, same here.", "Thanks for sharing!"]


class Command(BaseCommand):
	help = "Create a handful of demo users, posts, likes, comments, and friendships."

	def add_arguments(self, parser):
		parser.add_argument("--users", type=int, default=6, help="Number of users to create")
		parser.add_argument("--posts-per-user", type=int, default=2, help="Posts per user")

	def handle(self, *args, **options):
		num_users = min(options["users"], len(USERNAMES))
		posts_per_user = options["posts_per_user"]

		users = []
		for uname in USERNAMES[:num_users]:
			user, created = User.objects.get_or_create(username=uname, defaults={"email": f"{uname}@example.in"})
			if created:
				user.set_password(PASSWORD)
				user.save()
			users.append(user)

		posts = []
		for user in users:
			for _ in range(posts_per_user):
				post = Post.objects.create(user=user, content=random.choice(POST_SAMPLES))
				posts.append(post)

		for post in posts:
			likers = random.sample(users, k=random.randint(1, min(3, len(users))))
			for liker in likers:
				if liker != post.user:
					post.likes.add(liker)

			commenters = random.sample(users, k=random.randint(0, min(2, len(users))))
			for commenter in commenters:
				if commenter != post.user:
					Comment.objects.create(post=post, user=commenter, content=random.choice(COMMENT_SAMPLES))

		friendship_count = 0
		for i in range(len(users)):
			for j in range(i + 1, len(users)):
				if random.random() < 0.4:
					lo, hi = sorted([users[i].id, users[j].id])
					_, created = Friendship.objects.get_or_create(user1_id=lo, user2_id=hi)
					if created:
						friendship_count += 1

		self.stdout.write(self.style.SUCCESS(
			f"Seeded {len(users)} users (password: {PASSWORD}), {len(posts)} posts, {friendship_count} friendships."
		))