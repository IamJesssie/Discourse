from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

# FR-PE-001: Post model with edit tracking
class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    topic = models.ForeignKey('topic.Topic', on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edited_posts')
    is_deleted = models.BooleanField(default=False)

    # FR-PE-005: Time window validation method
    def is_editable_by(self, user):
        """Check if post is editable by given user based on permissions and time window"""
        from django.conf import settings
        if user.is_superuser or user.groups.filter(name='Moderators').exists():
            return True
            
        if self.author != user:
            return False
            
        # Get edit window from category or global settings
        edit_window = self.topic.category.post_edit_window_minutes or \
                    getattr(settings, 'POST_EDIT_WINDOW_MINUTES', 60)
                    
        time_since_creation = timezone.now() - self.created_at
        return time_since_creation.total_seconds() <= edit_window * 60

    # FR-PE-013: Content validation
    def clean(self):
        if len(self.content.strip()) == 0:
            raise ValidationError({'content': 'Post content cannot be empty'})

    def __str__(self):
        return f"Post #{self.id} in {self.topic.title}"
        
    def get_absolute_url(self):
        return reverse('post:edit_post', kwargs={'post_id': self.pk})

# FR-PE-009: Edit history tracking
class PostEditHistory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='edit_history')
    old_content = models.TextField()
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    edited_at = models.DateTimeField(auto_now_add=True)
    edit_reason = models.CharField(max_length=255, blank=True)

    # FR-PE-010: Diff generation support
    @property
    def content_diff(self):
        from difflib import unified_diff
        current = self.post.content.splitlines()
        previous = self.old_content.splitlines()
        return '\n'.join(unified_diff(previous, current))

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = "Post edit histories"

    def __str__(self):
        return f"Edit #{self.id} on Post {self.post.id}"
