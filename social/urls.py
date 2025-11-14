from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('signup/', views.signup, name='signup'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:post_id>/like-toggle/', views.post_like_toggle, name='post_like_toggle'),
    path('post/<int:post_id>/comment/', views.comment_add, name='comment_add'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('friend/request/<str:username>/', views.friend_request, name='friend_request'),
    path('friend/accept/<int:friendship_id>/', views.friend_accept, name='friend_accept'),
]
