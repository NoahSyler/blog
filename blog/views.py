from django.shortcuts import render, get_object_or_404

from .models import Post, Tag, Author




def starting_page(request):
    latest_posts = Post.objects.all().order_by('-date')[:3]
    return render(request, 'blog/index.html', {
        'posts' : latest_posts
        })

def posts(request):
    all_posts = Post.objects.all().order_by('-date')
    return render(request, 'blog/all-posts.html', {
        'all_posts': all_posts
    })


#COMMENT SECTION
#Create the forms file with Forms classes
#Form field needs to be in post html with csrf token
#Data should be sent to a comments model. I think this can be done with a function
#within the forms class, but I can't remember.

#READ LATER
#Add read later feature in post.html
#Session data needs to be configured in the setting.py file
#I think a session module should be made to use desired session functions
#It should be gathered with get, so that is it is not present, an error is not thrown

#UPLOAD PICTURES
#I need to review this feature. I will probably use UploadFileForm
#The file and url path will need to e configured




def post_detail(request, slug):
    identified_post = get_object_or_404(Post, slug=slug)
    #Post.objects.get(slug=slug)
    return render(request, 'blog/post-detail.html', {
        'post': identified_post,
        'post_tags': identified_post.tags.all()
    })
