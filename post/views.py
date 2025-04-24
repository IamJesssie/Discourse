from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Post, PostEditHistory
from .forms import PostEditForm, RevertConfirmationForm

# FR-PE-001: Post edit view with permission checks
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # FR-PE-005: Time window check
    if not post.is_editable_by(request.user):
        messages.error(request, "Editing time window has expired")
        return redirect(post.topic.get_absolute_url())

    if request.method == 'POST':
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            # FR-PE-008: Edit history tracking
            old_content = post.content
            edit_reason = form.cleaned_data.get('edit_reason', '')
            
            post = form.save(commit=False)
            post.modified_at = timezone.now()
            post.edited_by = request.user
            post.save()
            
            # Create edit history record
            PostEditHistory.objects.create(
                post=post,
                old_content=old_content,
                edited_by=request.user,
                edit_reason=edit_reason
            )
            
            messages.success(request, "Post updated successfully")
            return redirect(post.get_absolute_url())
    else:
        form = PostEditForm(instance=post)
    
    return render(request, 'post/edit.html', {
        'form': form,
        'post': post,
        'preview_content': post.content
    })

# FR-PE-011: Revert post view
@login_required
def revert_post(request, history_id):
    history = get_object_or_404(PostEditHistory, pk=history_id)
    
    # FR-PE-017: Permission check
    if not request.user.has_perm('post.change_post'):
        messages.error(request, "You don't have permission to revert posts")
        return redirect(history.post.get_absolute_url())
    
    if request.method == 'POST':
        form = RevertConfirmationForm(request.POST)
        if form.is_valid():
            # Save current content to history before reverting
            current_content = history.post.content
            PostEditHistory.objects.create(
                post=history.post,
                old_content=current_content,
                edited_by=request.user,
                edit_reason=f"Reverted to version {history_id}"
            )
            
            # Perform revert
            history.post.content = history.old_content
            history.post.modified_at = timezone.now()
            history.post.edited_by = request.user
            history.post.save()
            
            messages.success(request, "Post reverted to previous version")
            return redirect(history.post.get_absolute_url())
    
    return render(request, 'post/revert_confirm.html', {
        'history': history,
        'form': RevertConfirmationForm()
    })
