from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Group, Post, User, Comment
from .forms import PostForm, CommentForm


POST_COUNT = 10


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    paginator = Paginator(post_list, POST_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POST_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "group": group,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = User.objects.get(username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POST_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "author": author,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    context = {
        "post": post,
        "comments": comments,
        "form": CommentForm()
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "posts/create_post.html", {
            "form": form,
            "edit": False})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:profile', post.author)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save()
        return redirect("posts:post_detail", post_id=post.id)
    return render(
        request, "posts/create_post.html", {"form": form, "edit": True,
                                            'id_post': post.id}
    )

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    context = {}
    return render(request, 'posts/follow.html', context)

@login_required
def profile_follow(request, username):
    # Подписаться на автора
    ...

@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    ...
 