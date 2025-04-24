from django.contrib import admin
from .models import FoundItem, ClaimRequest

@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    """Admin interface for managing found items with TCD Baltazar standards"""
    list_display = ('title', 'status', 'found_date', 'reported_by', 'location', 'id_document')
    list_editable = ('status',)
    list_filter = ('status', 'found_date', 'location')
    search_fields = ('title', 'description', 'reported_by__username')
    raw_id_fields = ('reported_by',)
    date_hierarchy = 'found_date'
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'status')
        }),
        ('Discovery Details', {
            'fields': ('location', 'found_date', 'reported_by'),
            'classes': ('collapse',)
        }),
        ('Documentation', {
            'fields': ('id_document',),
            'classes': ('wide',)
        }),
    )
    list_per_page = 25
    list_select_related = ('reported_by',)
    actions = ['mark_as_claimed', 'archive_items']
    
    @admin.action(description='Mark selected items as claimed')
    def mark_as_claimed(self, request, queryset):
        queryset.update(status='CLAIMED')
        
    @admin.action(description='Archive selected items')
    def archive_items(self, request, queryset):
        queryset.update(status='ARCHIVED')

@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'claimant', 'status', 'claim_date')
    list_filter = ('status', 'claim_date')
    search_fields = ('item__title', 'claimant__username')
    raw_id_fields = ('item', 'claimant')