from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None):
        if not phone_number:
            raise ValueError('User must have a phone number')
        user = self.model(phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password):
        user = self.create_user(phone_number, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

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
    is_suspended = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)  # افزودن فیلد OTP

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
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
    is_active = models.BooleanField(default=True)


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


class Page(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)

    def __str__(self):
        return self.choice_text

class Response(models.Model):
    question = models.ForeignKey(Question, related_name='responses', on_delete=models.CASCADE)
    participant_id = models.CharField(max_length=255)
    answer_text = models.TextField()

    def __str__(self):
        return f"Response to {self.question} by {self.participant_id}"