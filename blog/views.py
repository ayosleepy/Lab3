from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Post, Like, Comment, Profile
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    PostForm, CommentForm
)


def index(request):
    posts_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts_list, 50)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'posts': posts,
    }
    return render(request, 'blog/index.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(user_posts, 50)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'posts': posts,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def delete_profile(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Ваш профиль удален.')
        return redirect('index')
    return render(request, 'blog/delete_profile.html')


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост опубликован!')
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост обновлен!')
            return redirect('index')
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост удален!')
        return redirect('index')

    return render(request, 'blog/delete_post.html', {'post': post})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()

    return redirect('index')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Комментарий добавлен!')

    return redirect('index')


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комментарий обновлен!')
            return redirect('index')
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/edit_comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('index')

    return render(request, 'blog/delete_comment.html', {'comment': comment})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} создан!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'blog/register.html', {'form': form})