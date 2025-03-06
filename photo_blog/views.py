from django.shortcuts import render, get_object_or_404
from .models import BlogPost


def blog_post_list(request):
    photo_blogs = BlogPost.objects.filter(active=True)
    context = {"photo_blogs": photo_blogs}
    return render(request, "photo_blog/post_list.html", context)


def blog_post_detail(request, slug):
    photo_blog = get_object_or_404(BlogPost, slug=slug, active=True)
    photo_blogs = BlogPost.objects.filter(active=True).exclude(id=photo_blog.id).order_by('-created_at')[:3]
    absolute_image_url = request.build_absolute_uri(photo_blog.image.url)
    context = {
        "photo_blog": photo_blog,
        "photo_blogs": photo_blogs,
        "absolute_image_url": absolute_image_url,
    }
    return render(request, "photo_blog/post_detail.html", context)
