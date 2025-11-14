from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
import random
from datetime import timedelta

from social.models import Post, Profile


USERNAMES = [
    "aarav", "vivaan", "aditya", "ishita", "ananya", "rohan",
    "priya", "rahul", "kavya", "tanvi", "harshit", "dhruv",
    "divyansh", "neha", "arjun",
]

POST_SAMPLES = [
    "Namaste from Delhi!",
    "Just had chai with friends.",
    "Exploring Bengaluru traffic 🚗",
    "Cricket day at the ground! 🏏",
    "Diwali vibes and lights everywhere ✨",
    "Monsoon rains in Mumbai ☔",
    "Campus life at PESU is awesome!",
    "Biryani or Pani Puri? Can't decide!",
    "Coding late night with chai.",
    "Weekend getaway to Coorg.",
]


class Command(BaseCommand):
    help = "Seed dummy Indian users and posts"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=8, help="Number of users to create")
        parser.add_argument("--posts-per-user", type=int, default=3, help="Posts per user")

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        num_users = min(options["users"], len(USERNAMES))
        ppu = options["posts_per_user"]

        created_users = 0
        created_posts = 0

        now = timezone.now()
        base_start = now - timedelta(days=30)

        for uname in USERNAMES[:num_users]:
            email = f"{uname}@example.in"
            user, u_created = User.objects.get_or_create(
                username=uname,
                defaults={
                    "email": email,
                },
            )
            if u_created:
                user.set_password("Password@123")
                # Spread join dates over the last month
                user.date_joined = base_start + timedelta(days=random.randint(0, 28))
                user.save()
                created_users += 1
            # Ensure a profile exists
            Profile.objects.get_or_create(user=user)

            # Create posts
            for i in range(ppu):
                content = random.choice(POST_SAMPLES)
                created_at = base_start + timedelta(days=random.randint(0, 28), hours=random.randint(0, 23))
                post = Post.objects.create(user=user, content=content, created_at=created_at)
                created_posts += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded users: {created_users}, posts: {created_posts}"
        ))
