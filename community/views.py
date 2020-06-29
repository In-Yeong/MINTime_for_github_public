from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment_P
from .forms import PostForm, Comment_P_Form
from movies.models import Movie, Review
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

# Create your views here.
def post_search(request):
    qs = Post.objects.all().order_by('-id')

    q = request.GET.get('q', '')
    if q: 
        qs = qs.filter(title__icontains=q)
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'posts' : qs,
        'q' : q,
        'page_obj' : page_obj,
    }

    return render(request, 'community/posts.html', context)

def posts(request):
    posts = Post.objects.all().order_by('-id')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'community/posts.html', context)

def pur_posts(request, purpose_pk):
    if int(purpose_pk) > 3:
        return redirect('community:posts')
    posts = Post.objects.filter(purpose=purpose_pk).order_by('-id')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'purpose_pk': purpose_pk,
    }
    return render(request, 'community/posts.html', context)
    
@login_required
def post_create(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community:post_detail', post.pk)
    else:
        form = PostForm()
    context = {
        'form': form
    }
    return render(request, 'community/form.html', context)

@login_required
def post_detail(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    form = Comment_P_Form()
    context = {
        'post': post,
        'form': form
    }
    return render(request, 'community/post_detail.html', context)

@login_required
def post_update(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.user == post.user:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                return redirect('community:post_detail', post.pk)
        else:
            form = PostForm(instance=post)
        context = {
            'form': form
        }
        return render(request, 'community/form.html', context)
    else:
        return redirect('community:post_detail', post.pk)

@login_required
def post_delete(request, post_pk):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_pk)
        if request.user == post.user:
            post.delete()
    return redirect('community:posts')

@login_required
def com_p_create(request, post_pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    post = get_object_or_404(Post, pk=post_pk)
    form = Comment_P_Form(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()
    return redirect('community:post_detail', post.pk)

@login_required
def com_p_delete(request, post_pk, comment_pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comment_P, pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
    return redirect('community:post_detail', post_pk)
