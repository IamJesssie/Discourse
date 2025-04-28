from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Topic, Category
from .forms import TopicCreationForm
from django.shortcuts import render

# New: Topic list view
@login_required
def topic_list(request):
    topics = Topic.objects.all().order_by('-created_at')
    return render(request, 'topic/topic_list.html', {
        'topics': topics
    })

# FR-TC-001: Topic creation view
@login_required
def create_topic(request):
    # FR-TC-007: Permission check
    if not request.user.has_perm('topic.add_topic'):
        messages.error(request, "You don't have permission to create topics.")
        return redirect('category_list')
    
    if request.method == 'POST':
        form = TopicCreationForm(request.POST)
        # FR-TC-003: Form validation
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            # FR-TC-005: Success message
            messages.success(request, 
                f'Topic created successfully! <a href="{topic.get_absolute_url()}">View topic</a><br><span class="text-sm text-gray-700">Note: Topic titles cannot be edited after creation.</span>')
            return redirect(topic.get_absolute_url())
    else:
        form = TopicCreationForm()
    
    # FR-TC-004: Preview functionality
    preview_content = request.POST.get('content', '') if request.method == 'POST' else ''
    return render(request, 'topic/create.html', {
        'form': form,
        'preview_content': preview_content
    })

# FR-TC-005: Topic detail view
def topic_detail(request, pk):
    import logging
    from django.conf import settings
    logger = logging.getLogger('topic.views')
    
    topic = get_object_or_404(Topic.objects.prefetch_related('posts'), pk=pk)
    
    # FR-PE-005: Check which posts are editable by the current user
    editable_posts = set()
    if request.user.is_authenticated:
        logger.info(f"Checking edit permissions for user {request.user.username} in topic {topic.id}")
        for post in topic.posts.all():
            is_editable = post.is_editable_by(request.user)
            logger.info(f"Post {post.id} editable: {is_editable}")
            if is_editable:
                editable_posts.add(post.id)
        
        logger.info(f"Editable posts for user {request.user.username}: {editable_posts}")
    
    return render(request, 'topic/topic_detail.html', {
        'topic': topic,
        'editable_posts': editable_posts,
        'POST_EDIT_WINDOW_MINUTES': getattr(settings, 'POST_EDIT_WINDOW_MINUTES', 2)
    })
