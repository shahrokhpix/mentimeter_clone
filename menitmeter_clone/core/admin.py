# core/admin.py

from django.contrib import admin
from .models import User, SubscriptionPackage, Survey

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone_number', 'subscription_type', 'subscription_expiration']
    search_fields = ['username', 'phone_number']

@admin.register(SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_in_months', 'max_surveys_per_month']

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'creation_date', 'editable_until']
    search_fields = ['title', 'creator__username']
