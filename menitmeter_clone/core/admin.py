# core/admin.py

from django.contrib import admin
from .models import User, SubscriptionPackage, Survey, Question, Choice, Response, Payment, Page
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'phone_number', 'subscription_type', 'subscription_expiration', 'is_suspended']
    search_fields = ['username', 'phone_number']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'avatar')}),
        ('اطلاعات اشتراک', {'fields': ('subscription_type', 'subscription_expiration', 'is_suspended')}),
        ('مجوزها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    actions = ['make_premium', 'suspend_users']

    def make_premium(self, request, queryset):
        queryset.update(subscription_type='semi_annual')
    make_premium.short_description = 'تبدیل به کاربر مادام العمر'

    def suspend_users(self, request, queryset):
        queryset.update(is_suspended=True)
    suspend_users.short_description = 'تعلیق کاربران انتخاب شده'

@admin.register(SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_in_months', 'max_surveys_per_month']

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'creation_date', 'editable_until', 'is_active']
    search_fields = ['title', 'creator__username']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'survey', 'question_type']
    search_fields = ['question_text', 'survey__title']

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question']
    search_fields = ['choice_text', 'question__question_text']

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['question', 'participant_id', 'answer_text']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'status', 'created_at']
    search_fields = ['user__username', 'package__name']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
