from django.contrib import admin
from .models import Post, PostEditHistory
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

# FR-PE-009: Post edit history inline
class PostEditHistoryInline(admin.TabularInline):
    model = PostEditHistory
    extra = 0
    readonly_fields = ('edited_by', 'edited_at', 'edit_reason', 'old_content', 'content_diff')
    can_delete = False

    def content_diff(self, instance):
        return format_html('<pre>{}</pre>', instance.content_diff)
    content_diff.short_description = 'Content Diff'

# FR-PE-001: Post admin interface
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for post management with TCD Baltazar standards"""
    list_display = ('content_preview', 'author', 'topic', 'created_at', 'modified_at', 'is_deleted')
    list_filter = ('author', 'topic', 'created_at', 'is_deleted', 'modified_at')
    search_fields = ('content', 'topic__title', 'author__username')
    raw_id_fields = ('author', 'topic', 'edited_by')
    date_hierarchy = 'created_at'
    list_editable = ('is_deleted',)
    fieldsets = (
        (None, {
            'fields': ('content', 'topic', 'author')
        }),
        ('Moderation', {
            'fields': ('is_deleted', 'edited_by', 'modified_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 25
    view_on_site = True
    show_full_result_count = False
    inlines = [PostEditHistoryInline]
    actions = ['mark_deleted', 'restore_post']
    
    # FR-PE-006: Moderator permissions
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_deleted=False)
        return qs

    def content_preview(self, obj):
        return f"{obj.content[:50]}..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    # FR-PE-012: Content sanitization in admin
    def save_model(self, request, obj, form, change):
        if change:
            obj.edited_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description='Mark selected posts as deleted')
    def mark_deleted(self, request, queryset):
        queryset.update(is_deleted=True)

    @admin.action(description='Restore selected posts')
    def restore_post(self, request, queryset):
        queryset.update(is_deleted=False)

# FR-PE-009: Edit history admin
@admin.register(PostEditHistory)
class PostEditHistoryAdmin(admin.ModelAdmin):
    list_display = ('post_link', 'edited_by', 'edited_at', 'edit_reason')
    readonly_fields = ('post', 'old_content', 'edited_by', 'edited_at', 'content_diff')
    list_filter = ('edited_at', 'edited_by')
    date_hierarchy = 'edited_at'

    def post_link(self, obj):
        url = reverse('admin:post_post_change', args=[obj.post.id])
        return mark_safe(f'<a href="{url}">Post #{obj.post.id}</a>')
    post_link.short_description = 'Post'

    def content_diff(self, instance):
        return format_html('<pre>{}</pre>', instance.content_diff)
    content_diff.short_description = 'Content Diff'
