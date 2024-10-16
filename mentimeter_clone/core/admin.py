# core/admin.py

from django.contrib import admin
from .models import User, SubscriptionPackage, Survey, Question, Choice, Response, Payment, Page
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['phone_number', 'first_name', 'last_name', 'subscription_type', 'subscription_expiration', 'is_suspended']
    search_fields = ['phone_number', 'first_name', 'last_name']
    list_filter = ['subscription_type', 'is_suspended']
    fieldsets = (
        (_('اطلاعات کاربری'), {'fields': ('phone_number', 'password')}),
        (_('اطلاعات شخصی'), {'fields': ('first_name', 'last_name', 'avatar')}),
        (_('اشتراک'), {'fields': ('subscription_type', 'subscription_expiration', 'is_suspended')}),
        (_('مجوزها'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('تاریخ‌ها'), {'fields': ('last_login', 'date_joined')}),
    )
    ordering = ['phone_number']
    actions = ['make_premium', 'suspend_users']

    def make_premium(self, request, queryset):
        queryset.update(subscription_type='semi_annual')
    make_premium.short_description = 'تبدیل به کاربر مادام‌العمر'

    def suspend_users(self, request, queryset):
        queryset.update(is_suspended=True)
    suspend_users.short_description = 'تعلیق کاربران انتخاب شده'

@admin.register(SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_in_months', 'max_surveys_per_month']
    search_fields = ['name']
    list_filter = ['duration_in_months']

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'creation_date', 'editable_until', 'is_active']
    search_fields = ['title', 'creator__phone_number']
    list_filter = ['is_active', 'creation_date']
    actions = ['duplicate_surveys', 'delete_selected']

    def duplicate_surveys(self, request, queryset):
        for survey in queryset:
            survey.pk = None
            survey.title += ' (کپی)'
            survey.creation_date = timezone.now().date()
            survey.editable_until = timezone.now().date() + timedelta(days=30)
            survey.save()
    duplicate_surveys.short_description = "تکثیر نظرسنجی‌های انتخاب شده"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'survey', 'question_type']
    search_fields = ['question_text', 'survey__title']
    list_filter = ['question_type']

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question']
    search_fields = ['choice_text', 'question__question_text']
    list_filter = ['question']

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['question', 'participant_id', 'submitted_choice']
    search_fields = ['participant_id', 'question__question_text']
    list_filter = ['question']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'status', 'created_at']
    search_fields = ['user__phone_number', 'package__name']
    list_filter = ['status', 'created_at']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    list_filter = ['created_at']
