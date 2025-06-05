from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from .models import Post, Like

@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')

    user_liked_posts = []
    if request.user.is_authenticated:
        user_liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)

    # ✅ Add this loop to attach liked usernames to each post
    for post in posts:
        likes = post.likes.all()
        liked_users = [like.user for like in likes]
        post.like_count = likes.count()

        if liked_users:
            post.first_liker = liked_users[0]
            post.other_likers_count = len(liked_users) - 1
        else:
            post.first_liker = None
            post.other_likers_count = 0

    return render(request, 'socialapp/home.html', {
        'posts': posts,
        'user_liked_posts': user_liked_posts,
    })

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'socialapp/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'socialapp/login.html', {'error': 'Invalid credentials'})
        else:
            return render(request, 'socialapp/login.html', {'error': 'Please fill all fields'})

    return render(request, 'socialapp/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

# socialapp/views.py
from django.shortcuts import render, redirect
from .forms import PostForm
from django.contrib.auth.decorators import login_required

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user   # 👈 Important line
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'socialapp/create_post.html', {'form': form})

from django.shortcuts import get_object_or_404
from .forms import PostForm

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return HttpResponse("You are not allowed to edit this post.")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PostForm(instance=post)

    return render(request, 'socialapp/edit_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return HttpResponse("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'socialapp/delete_post.html', {'post': post})


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, Post, Like  # 🔸 Make sure Like is imported

def profile_view(request, username):
    from django.contrib.auth.models import User
    profile_user = User.objects.get(username=username)
    profile = profile_user.profile
    posts = Post.objects.filter(user=profile_user)

    user_liked_posts = []
    if request.user.is_authenticated:
        user_liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)

    for post in posts:
        likes = post.likes.all()
        liked_users = [like.user for like in likes]  # full User objects
        post.like_count = likes.count()

        if liked_users:
            post.first_liker = liked_users[0]  # First user who liked
            post.other_likers_count = len(liked_users) - 1
        else:
            post.first_liker = None
            post.other_likers_count = 0

    return render(request, 'socialapp/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'user_liked_posts': user_liked_posts,
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import UserProfileForm
from django.http import HttpResponseForbidden


@login_required
def edit_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user != profile_user:
        return HttpResponseForbidden("Not allowed")

    profile = profile_user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=profile_user.username)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'socialapp/edit_profile.html', {'form': form, 'profile_user': profile_user})

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Profile
from django.contrib.auth.models import User

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        return HttpResponseForbidden("You cannot follow yourself.")
    if request.method != 'POST':
        return HttpResponseForbidden("Only POST requests allowed.")
    user_profile = Profile.objects.get(user=user_to_follow)
    user_profile.followers.add(request.user)
    return redirect('profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    if user_to_unfollow == request.user:
        return HttpResponseForbidden("You cannot unfollow yourself.")
    if request.method != 'POST':
        return HttpResponseForbidden("Only POST requests allowed.")
    user_profile = Profile.objects.get(user=user_to_unfollow)
    user_profile.followers.remove(request.user)
    return redirect('profile', username=username)

def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    followers = profile.followers.all()
    return render(request, 'socialapp/followers_list.html', {'profile_user': user, 'followers': followers})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

def following_list(request, username):
    user = get_object_or_404(User, username=username)
    following = User.objects.filter(profile__followers=user)

    return render(request, 'socialapp/following_list.html', {
        'profile_user': user,
        'following': following,
    })

def user_list(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'socialapp/user_list.html', {'users': users})

from django.shortcuts import get_object_or_404, redirect
from .models import Post, Like

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()  # Unlike
    return redirect('home')  # Or redirect to 'profile', etc.

from django.shortcuts import get_object_or_404, redirect
from .models import Post, Comment

def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content")
        Comment.objects.create(post=post, user=request.user, content=content)
    return redirect('home')






