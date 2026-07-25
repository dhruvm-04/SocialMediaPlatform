from django.contrib import admin

from .models import Comment, Friendship, Post


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
	list_display = ("user1", "user2", "created_at")
	search_fields = ("user1__username", "user2__username")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "created_at")
	search_fields = ("user__username", "content")
	list_filter = ("created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "post", "created_at")
	search_fields = ("user__username", "content")
	list_filter = ("created_at",)