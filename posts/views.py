from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_COUNT

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def server_error(request):
    return render(request, 'misc/500.html', status=500)


def page_not_found(request, exception):
    return render(request,
                  'misc/404.html',
                  {"path": request.path},
                  status=404)


def index(request):
    posts = Post.objects.all().select_related('group')
    paginator = Paginator(posts, POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page,
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page,
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    paginator = Paginator(author.posts.all(), POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = Follow.objects.filter(user__username=request.user.username,
                                      author=author).exists()
    return render(request, 'profile.html', {'page': page,
                                            'author': author,
                                            'following': following})


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post, author__username=username, id=post_id)
    author = post.author
    comments = post.comments.all()
    paginator = Paginator(comments, POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = CommentForm(request.POST or None)
    following = Follow.objects.filter(user__username=request.user.username,
                                      author=author).exists()
    return render(request, 'post.html', {'post': post,
                                         'author': author,
                                         'page': page,
                                         'form': form,
                                         'comments': comments,
                                         'following': following})


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('posts:post_view', username=username, post_id=post_id)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form, 'post': post})
    form.save()
    return redirect('posts:post_view', username=username, post_id=post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    paginator = Paginator(post.comments.all(), POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if not form.is_valid():
        return render(request, 'post.html', {'form': form,
                                             'post': post,
                                             'page': page,
                                             'author': post.author})
    new_comment = form.save(commit=False)
    new_comment.author = request.user
    new_comment.post = post
    new_comment.save()
    return redirect('posts:post_view', username=username, post_id=post_id)


@login_required
def follow_index(request):
    paginator = Paginator(Post.objects.filter(
        author__following__user=request.user
    ), POSTS_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    if request.user.username != username:
        author = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    if request.user.username != username:
        author = get_object_or_404(User, username=username)
        get_object_or_404(Follow, user__username=request.user.username,
                          author=author).delete()
    return redirect('posts:profile', username=username)
