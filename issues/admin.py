from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Ward, Department, Issue, Upvote, StatusHistory


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'assigned_ward', 'phone_number', 'is_staff']
    list_filter = ['role', 'assigned_ward', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Civic Role & Ward Assignment', {'fields': ('role', 'phone_number', 'assigned_ward', 'assigned_department', 'designation')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Civic Role & Ward Assignment', {'fields': ('role', 'phone_number', 'assigned_ward', 'assigned_department', 'designation')}),
    )


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['ward_number', 'name', 'city_corporation', 'councillor_name', 'contact_phone', 'total_issues_count', 'resolution_rate']
    search_fields = ['ward_number', 'name', 'councillor_name', 'city_corporation']
    list_filter = ['city_corporation']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'emergency_hotline', 'contact_email']
    search_fields = ['name', 'code']


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ['changed_by', 'old_status', 'new_status', 'comment', 'proof_photo', 'timestamp']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'severity', 'ward', 'status', 'verification_status', 'upvotes_count', 'created_at']
    list_filter = ['status', 'category', 'severity', 'ward', 'verification_status']
    search_fields = ['title', 'description', 'address', 'reporter_name']
    inlines = [StatusHistoryInline]


@admin.register(Upvote)
class UpvoteAdmin(admin.ModelAdmin):
    list_display = ['issue', 'user', 'session_key', 'created_at']


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['issue', 'changed_by', 'old_status', 'new_status', 'timestamp']
    list_filter = ['old_status', 'new_status', 'timestamp']
