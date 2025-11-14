import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from social.models import Post, Comment, Like, Profile

NEW_USERNAMES = ["meera", "kartik", "nisha", "sanjay", "pooja"]
COMMENTS = [
    "Nice post!",
    "Interesting thoughts.",
    "Thanks for sharing!",
    "Agreed!",
    "🔥",
]

class Command(BaseCommand):
    help = "Create 5 dummy users with 1 post each, add random likes and comments. Re-running always adds one new post per listed user."

    def handle(self, *args, **options):
        User = get_user_model()
        created_users = 0
        created_posts = 0
        created_likes = 0
        created_comments = 0

        # Track posts created in this run only
        new_posts = []

        for uname in NEW_USERNAMES:
            user, was_created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': f"{uname}@example.in",
                }
            )
            if was_created:
                user.set_password("Password@123")
                user.save()
                Profile.objects.get_or_create(user=user)
                created_users += 1

            # Always create exactly one new post for this user on every run
            post = Post.objects.create(user=user, content=f"Hello from {uname}!", created_at=timezone.now())
            created_posts += 1
            new_posts.append(post)

        all_users = list(User.objects.all())

        for post in new_posts:
            # Random likes from other users (1-3 likes)
            likers = random.sample(all_users, k=min(max(1, random.randint(1, 3)), len(all_users)))
            for liker in likers:
                if liker == post.user:
                    continue
                _, created = Like.objects.get_or_create(user=liker, post=post)
                if created:
                    created_likes += 1
            # Random comments (0-2 comments)
            commenter_count = random.randint(0, 2)
            commenters = random.sample(all_users, k=min(commenter_count, len(all_users)))
            for commenter in commenters:
                if commenter == post.user:
                    continue
                Comment.objects.create(user=commenter, post=post, content=random.choice(COMMENTS))
                created_comments += 1

        self.stdout.write(self.style.SUCCESS(
            f"Added users: {created_users}, posts: {created_posts}, likes: {created_likes}, comments: {created_comments}"
        ))
