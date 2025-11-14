from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create or update the 'super' superuser with predefined password"

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'super'
        password = 'Super@1234'
        email = 'super@example.com'
        user, created = User.objects.get_or_create(username=username, defaults={
            'email': email,
            'is_staff': True,
            'is_superuser': True,
        })
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Created superuser 'super' with password 'Super@1234'"))
        else:
            # Ensure flags and password
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.WARNING("Updated existing user 'super' to superuser with password 'Super@1234'"))
