from django.contrib import admin
from .models import Category, Topic

# FR-TC-002: Category admin interface
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for managing discussion categories"""
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'updated_at')
    filter_horizontal = ('allowed_groups',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Permissions', {
            'fields': ('allowed_groups', 'require_tag', 'max_tags'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

# FR-TC-001: Topic admin interface
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'is_locked')
    list_display_links = ('title',)
    raw_id_fields = ('author', 'category')
    date_hierarchy = 'created_at'
    list_editable = ('is_locked',)
    list_filter = ('category', 'is_locked', 'created_at')
    search_fields = ('title', 'tags')
    readonly_fields = ('created_at', 'modified_at')
    
    fieldsets = (
        (None, {'fields': ('title', 'content', 'category', 'author')}),
        ('Options', {'fields': ('tags', 'notify_on_reply', 'is_locked')}),
        ('Timestamps', {'fields': ('created_at', 'modified_at')}),
    )
