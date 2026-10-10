from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *


# ============================================================
# CUSTOM USER ADMIN
# ============================================================

class UserAdmin(BaseUserAdmin):

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Info', {
            'fields': ('role',),
        }),
    )

    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_staff',
        'is_active',
    ]

    list_filter = [
        'role',
        'is_staff',
        'is_superuser',
        'is_active',
    ]

    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
    ]

    ordering = ['username']

    list_per_page = 15


# ============================================================
# MEMBER PROFILE ADMIN
# ============================================================

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'full_name',
        'mobile',
        'plan',
        'join_date',
    ]

    search_fields = [
        'user__username',
        'full_name',
        'mobile',
    ]

    list_filter = [
        'plan',
        'join_date',
    ]

    ordering = ['-join_date']

    list_per_page = 15

    date_hierarchy = 'join_date'


# ============================================================
# ENQUIRY ADMIN
# ============================================================

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'email',
        'mobile',
        'status',
        'created_at',
    ]

    search_fields = [
        'name',
        'email',
        'mobile',
    ]

    list_filter = [
        'status',
        'created_at',
    ]

    ordering = ['-created_at']

    list_per_page = 15

    date_hierarchy = 'created_at'


# ============================================================
# MEMBERSHIP PLAN
# ============================================================

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):

    list_display = [
        field.name
        for field in MembershipPlan._meta.fields
    ]

    list_per_page = 15


# ============================================================
# TRAINER
# ============================================================

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):

    list_display = [
        field.name
        for field in Trainer._meta.fields
    ]

    search_fields = [
        field.name
        for field in Trainer._meta.fields
        if field.get_internal_type() in ['CharField', 'EmailField']
    ]

    list_per_page = 15


# ============================================================
# EQUIPMENT
# ============================================================

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):

    list_display = [
        field.name
        for field in Equipment._meta.fields
    ]

    search_fields = [
        field.name
        for field in Equipment._meta.fields
        if field.get_internal_type() == 'CharField'
    ]

    list_per_page = 15


# ============================================================
# ATTENDANCE
# ============================================================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = [
        field.name
        for field in Attendance._meta.fields
    ]

    list_filter = [
        field.name
        for field in Attendance._meta.fields
        if field.get_internal_type() in ['DateField', 'DateTimeField', 'BooleanField']
    ]

    ordering = [
        field.name
        for field in Attendance._meta.fields
        if field.get_internal_type() in ['DateField', 'DateTimeField']
    ]

    list_per_page = 20


# ============================================================
# FEEDBACK
# ============================================================

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):

    list_display = [
        field.name
        for field in Feedback._meta.fields
    ]

    search_fields = [
        field.name
        for field in Feedback._meta.fields
        if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']
    ]

    list_per_page = 15


# ============================================================
# PAYMENT
# ============================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = [
        field.name
        for field in Payment._meta.fields
    ]

    list_filter = [
        field.name
        for field in Payment._meta.fields
        if field.get_internal_type() in [
            'DateField',
            'DateTimeField',
            'BooleanField',
        ]
    ]

    ordering = [
        field.name
        for field in Payment._meta.fields
        if field.get_internal_type() in [
            'DateField',
            'DateTimeField',
        ]
    ]

    list_per_page = 15


# ============================================================
# WORKOUT PLAN
# ============================================================

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):

    list_display = [
        field.name
        for field in WorkoutPlan._meta.fields
    ]

    search_fields = [
        field.name
        for field in WorkoutPlan._meta.fields
        if field.get_internal_type() in ['CharField', 'TextField']
    ]

    list_per_page = 15


# ============================================================
# USER
# ============================================================

admin.site.register(User, UserAdmin)


# ============================================================
# ADMIN SITE CONFIGURATION
# ============================================================

admin.site.site_header = "🏋️ My Gym Management"
admin.site.site_title = "My Gym Admin"
admin.site.index_title = "Gym Management Dashboard"