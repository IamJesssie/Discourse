from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.urls import reverse

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
        """Check if post is editable by given user based on permissions and time window (from last edit)"""
        from django.conf import settings
        import logging
        from datetime import datetime, timedelta
        logger = logging.getLogger('post.models')
        
        # Superusers and moderators can always edit
        if user.is_superuser or user.groups.filter(name='Moderators').exists():
            logger.info(f"User {user} is superuser/moderator, can edit post {self.id}")
            return True
        
        # Check if user is the author
        if self.author != user:
            logger.info(f"User {user} is not the author of post {self.id}")
            return False
        
        # Calculate time window 
        global_setting = getattr(settings, 'POST_EDIT_WINDOW_MINUTES', 2)
        category_setting = self.topic.category.post_edit_window_minutes
        edit_window = category_setting if category_setting is not None else global_setting
        
        # Get current time and last edit time
        now = timezone.now()
        last_edit_time = self.modified_at or self.created_at
        
        # Calculate the cutoff time by adding the edit window to the last edit time
        cutoff_time = last_edit_time + timedelta(minutes=edit_window)
        
        # Post is editable if current time is before cutoff time
        editable = now <= cutoff_time
        
        logger.info(
            f"Post {self.id} edit window check:\n"
            f"Now: {now}\n"
            f"Last edit: {last_edit_time}\n"
            f"Edit window: {edit_window} minutes\n"
            f"Cutoff time: {cutoff_time}\n"
            f"Editable: {editable}"
        )
        
        return editable

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
