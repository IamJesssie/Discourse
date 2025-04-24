from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

# FR-TC-002: Category model for topic organization
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allowed_groups = models.ManyToManyField('auth.Group', blank=True)
    require_tag = models.BooleanField(default=False)
    max_tags = models.PositiveIntegerField(default=5)
    post_edit_window_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Category-specific edit window in minutes (overrides global setting)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        verbose_name = "Category"

# FR-TC-001: Core topic model
class Topic(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=255, blank=True)
    notify_on_reply = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    # FR-TC-008: Title validation
    def clean(self):
        if len(self.title) < 15:
            raise ValidationError({'title': 'Title must be at least 15 characters long.'})
        if len(self.title) > 255:
            raise ValidationError({'title': 'Title cannot exceed 255 characters.'})

    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('topic:topic_detail', kwargs={'pk': self.pk})
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('topic:topic_detail', kwargs={'pk': self.pk})

# FR-TC-013: Title editing prohibition
def prevent_topic_title_update(sender, instance, **kwargs):
    if instance.pk:
        original = Topic.objects.get(pk=instance.pk)
        if instance.title != original.title:
            raise ValidationError("Topic titles cannot be modified after creation")

models.signals.pre_save.connect(prevent_topic_title_update, sender=Topic)
