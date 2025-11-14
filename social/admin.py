from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Profile, Post, Friendship, Like, Comment, Notification
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	fieldsets = (
		(None, {"fields": ("username", "password")}),
		("Personal info", {"fields": ("first_name", "last_name", "email", "dob", "gender")}),
		(
			"Permissions",
			{
				"fields": (
					"is_active",
					"is_staff",
					"is_superuser",
					"groups",
					"user_permissions",
				)
			},
		),
		("Important dates", {"fields": ("last_login", "date_joined")}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'password1', 'password2', 'dob', 'gender'),
		}),
	)
	list_display = ("username", "email", "first_name", "last_name", "is_staff")
	search_fields = ("username", "first_name", "last_name", "email")
	ordering = ("username",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "bio")
	search_fields = ("user__username", "user__email", "bio")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "created_at")
	search_fields = ("user__username", "content")
	list_filter = ("created_at",)


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
	list_display = ("user1", "user2", "status", "created_at")
	list_filter = ("status",)
	search_fields = ("user1__username", "user2__username")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
	list_display = ("user", "post", "created_at")
	search_fields = ("user__username",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "post", "created_at")
	search_fields = ("user__username", "content")
	list_filter = ("created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "message", "created_at", "read")
	list_filter = ("read", "created_at")
	search_fields = ("user__username", "message")

