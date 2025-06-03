from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_post, name='create_post'),
    path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),  # 👈 New line
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit-profile/<str:username>/', views.edit_profile, name='edit_profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('users/', views.user_list, name='user_list'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
]
