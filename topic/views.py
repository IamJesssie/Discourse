from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Topic, Category
from .forms import TopicCreationForm
from django.shortcuts import render

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
                f'Topic created successfully! <a href="{topic.get_absolute_url()}">View topic</a>')
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
    topic = get_object_or_404(Topic.objects.prefetch_related('posts'), pk=pk)
    return render(request, 'topic/topic_detail.html', {
        'topic': topic
    })
