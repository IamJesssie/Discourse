from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from .forms import PostCreateForm, PostEditForm
from topic.models import Topic
from django.utils import timezone
from django.conf import settings
import os
from .models import PostEditHistory
from .forms import RevertConfirmationForm

# FR-PE-001: Post edit view with permission checks
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # FR-PE-005: Time window check
    if not post.is_editable_by(request.user):
        messages.error(request, "Editing time window has expired")
        return redirect(post.topic.get_absolute_url())

    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            old_content = post.content
            edit_reason = form.cleaned_data.get('edit_reason', '')
            new_content = form.cleaned_data['content']
            post = form.save(commit=False)
            post.content = new_content  # Always update content from form

            uploaded_image = request.FILES.get('image')
            if uploaded_image:
                if settings.TESTING:
                    image_html = f'<img src="/media/uploads/{uploaded_image.name}" alt="{uploaded_image.name}" class="post-image" />'
                    if not post.content.endswith('\n'):
                        post.content += '\n'
                    post.content += image_html
                else:
                    media_dir = os.path.join(settings.BASE_DIR, 'media', 'uploads')
                    os.makedirs(media_dir, exist_ok=True)
                    image_path = os.path.join('uploads', uploaded_image.name)
                    full_path = os.path.join(settings.BASE_DIR, 'media', image_path)
                    with open(full_path, 'wb+') as destination:
                        for chunk in uploaded_image.chunks():
                            destination.write(chunk)
                    image_html = f'<img src="/media/{image_path}" alt="{uploaded_image.name}" class="post-image" />'
                    if not post.content.endswith('\n'):
                        post.content += '\n'
                    post.content += image_html
            post.modified_at = timezone.now()
            post.edited_by = request.user
            post.save()
            PostEditHistory.objects.create(
                post=post,
                old_content=old_content,
                edited_by=request.user,
                edit_reason=edit_reason
            )
            messages.success(request, "Post updated successfully")
            return redirect(post.topic.get_absolute_url())
    else:
        form = PostEditForm(instance=post)
    
    return render(request, 'post/edit.html', {
        'form': form,
        'post': post,
        'preview_content': post.content
    })

# C3257: View post revision history
@login_required
def post_history(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if user has permission to view history
    if not (request.user.is_superuser or request.user.groups.filter(name='Moderators').exists() or post.author == request.user):
        messages.error(request, "You don't have permission to view this post's history")
        return redirect(post.topic.get_absolute_url())
    
    # Get all revisions for this post
    history_entries = PostEditHistory.objects.filter(post=post).order_by('-edited_at')
    
    # Determine if user can revert posts
    can_revert = request.user.has_perm('post.change_post') or request.user.is_superuser or request.user.groups.filter(name='Moderators').exists()
    
    return render(request, 'post/history.html', {
        'post': post,
        'history_entries': history_entries,
        'can_revert': can_revert
    })

# FR-PE-011: Revert post view
@login_required
def revert_post(request, history_id):
    history = get_object_or_404(PostEditHistory, pk=history_id)
    
    # FR-PE-017: Permission check
    if not (request.user.has_perm('post.change_post') or 
            request.user.is_superuser or 
            request.user.groups.filter(name='Moderators').exists()):
        messages.error(request, "You don't have permission to revert posts")
        return redirect(history.post.topic.get_absolute_url())
    
    if request.method == 'POST':
        form = RevertConfirmationForm(request.POST)
        if form.is_valid():
            # Save current content to history before reverting
            current_content = history.post.content
            PostEditHistory.objects.create(
                post=history.post,
                old_content=current_content,
                edited_by=request.user,
                edit_reason=f"Reverted to version from {history.edited_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            # Perform revert
            history.post.content = history.old_content
            history.post.modified_at = timezone.now()
            history.post.edited_by = request.user
            history.post.save()
            
            messages.success(request, "Post reverted to previous version")
            return redirect(history.post.topic.get_absolute_url())
    else:
        form = RevertConfirmationForm()
    
    return render(request, 'post/revert_confirm.html', {
        'history': history,
        'form': form
    })

@login_required
def create_post(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    if topic.is_locked:
        messages.error(request, "This topic is locked. Replies are not allowed.")
        return redirect(topic.get_absolute_url())
    
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.topic = topic
            
            # Handle image upload
            uploaded_image = request.FILES.get('image')
            if uploaded_image:
                if settings.TESTING:
                    image_html = f'<img src="/media/uploads/{uploaded_image.name}" alt="{uploaded_image.name}" class="post-image" />'
                    if not post.content.endswith('\n'):
                        post.content += '\n'
                    post.content += image_html
                else:
                    media_dir = os.path.join(settings.BASE_DIR, 'media', 'uploads')
                    os.makedirs(media_dir, exist_ok=True)
                    image_path = os.path.join('uploads', uploaded_image.name)
                    full_path = os.path.join(settings.BASE_DIR, 'media', image_path)
                    with open(full_path, 'wb+') as destination:
                        for chunk in uploaded_image.chunks():
                            destination.write(chunk)
                    image_html = f'<img src="/media/{image_path}" alt="{uploaded_image.name}" class="post-image" />'
                    if not post.content.endswith('\n'):
                        post.content += '\n'
                    post.content += image_html
            
            post.save()
            messages.success(request, "Reply posted successfully.")
            return redirect(topic.get_absolute_url())
    else:
        form = PostCreateForm()
    
    return render(request, 'post/create_post.html', {'form': form, 'topic': topic})
