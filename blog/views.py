from typing import Any, Dict
#from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from django.views import View

from .models import Post
from .forms import CommentForm


class StartingPageView(ListView):
    template_name = 'blog/index.html'
    model = Post
    ordering = ['-date']
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:3]
        return data


class AllPostsView(ListView):
    template_name = 'blog/all-posts.html'
    model = Post
    ordering = ['-date']
    context_object_name = 'all_posts'


class SinglePostView(View):
    template_name = 'blog/post-detail.html'
    model = Post

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        context = {
            'post': post,
            'post_tags': post.tags.all(),
            'comment_form': CommentForm()
        }
        return render(request, 'blog/post-detail.html', context)

    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment_form.save()
            return HttpResponseRedirect(reverse('post-detail-page', args=[slug]))
        else:
            context = {
            'post': post,
            'post_tags': post.tags.all(),
            'comment_form': CommentForm()
            }
            return render(request, 'blog/post-detail.html', context)

'''
The function based views are no longer being used
'''


def starting_page(request):
    latest_posts = Post.objects.all().order_by('-date')[:3]
    return render(request, 'blog/index.html', {
        'posts': latest_posts
    })


def posts(request):
    all_posts = Post.objects.all().order_by('-date')
    return render(request, 'blog/all-posts.html', {
        'all_posts': all_posts
    })


def post_detail(request, slug):
    identified_post = get_object_or_404(Post, slug=slug)
    # Post.objects.get(slug=slug)
    return render(request, 'blog/post-detail.html', {
        'post': identified_post,
        'post_tags': identified_post.tags.all()
    })
