from django.urls import path
from . import views

# the slug trnasfomer ensures the concrete value that is past is a text
# that only contains letters, numbers, or dashes. The 'slug' format (It is SEO friendly)
urlpatterns = [
    path('', views.starting_page, name = 'starting-page'),
    path('posts', views.posts, name = 'posts-page'),
    path('posts/<slug:slug>', views.post_detail, name='posts-detail-page')
    ]
