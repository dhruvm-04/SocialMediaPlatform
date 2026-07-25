from django.urls import path

from . import views

urlpatterns = [
	path("", views.home, name="home"),
	path("register/", views.register, name="register"),
	path("profile/<str:username>/", views.profile, name="profile"),
	path("post/create/", views.post_create, name="post_create"),
	path("post/<int:post_id>/edit/", views.post_edit, name="post_edit"),
	path("post/<int:post_id>/delete/", views.post_delete, name="post_delete"),
	path("post/<int:post_id>/like-toggle/", views.post_like_toggle, name="post_like_toggle"),
	path("post/<int:post_id>/comment/", views.comment_add, name="comment_add"),
	path("friend/add/<str:username>/", views.friend_add, name="friend_add"),
	path("friend/remove/<str:username>/", views.friend_remove, name="friend_remove"),
]