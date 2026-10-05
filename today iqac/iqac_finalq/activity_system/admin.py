from django.contrib import admin
from .models import User, Activity


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'role', 'department', 'email', 'is_active')
    list_filter = ('role', 'department', 'is_active')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('department', 'role', 'username')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'faculty', 'department', 'sheet_name', 'category', 'academic_year', 'status', 'created_at')
    list_filter = ('department', 'category', 'status', 'academic_year', 'sheet_name')
    search_fields = ('faculty__username', 'faculty__full_name', 'title', 'sheet_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_iqac_approved', 'mark_rejected']

    def mark_iqac_approved(self, request, queryset):
        queryset.update(status='IQAC_APPROVED')
        self.message_user(request, f"{queryset.count()} activities marked as IQAC Approved.")
    mark_iqac_approved.short_description = "Mark selected as IQAC Approved"

    def mark_rejected(self, request, queryset):
        queryset.update(status='REJECTED')
        self.message_user(request, f"{queryset.count()} activities rejected.")
    mark_rejected.short_description = "Reject selected activities"
