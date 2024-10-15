from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    subscription_type = models.CharField(max_length=50, choices=[
        ('free', 'Free'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual')
    ])
    subscription_expiration = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username
class SubscriptionPackage(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    duration_in_months = models.IntegerField()
    max_surveys_per_month = models.IntegerField()

    def __str__(self):
        return self.name
class Survey(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add=True)
    editable_until = models.DateField()

    def is_editable(self):
        """کاربران فقط می‌توانند نظرسنجی‌ها را تا یک ماه ویرایش کنند"""
        return self.editable_until >= timezone.now()

    def __str__(self):
        return self.title
class Question(models.Model):
    SURVEY_TYPE_CHOICES = [
        ('word_cloud', 'Word Cloud'),
        ('poll', 'Poll'),
        ('scale', 'Scale'),
        ('ranking', 'Ranking'),
        ('video', 'Video'),
    ]
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=50, choices=SURVEY_TYPE_CHOICES)

    def __str__(self):
        return self.question_text
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE)
    authority = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment {self.id} - {self.user.username}'       