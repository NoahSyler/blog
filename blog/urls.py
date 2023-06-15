from django.urls import path
from . import views

# the slug trnasfomer ensures the concrete value that is past is a text
# that only contains letters, numbers, or dashes. The 'slug' format (It is SEO friendly)
urlpatterns = [
    path('', views.StartingPageView.as_view(), name = 'starting-page'),
    path('posts', views.AllPostsView.as_view(), name = 'posts-page'),
    path('posts/<slug:slug>', views.SinglePostView.as_view(), name='post-detail-page')
    ]
