# core/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        """
        ایجاد یک کاربر جدید با شماره موبایل و رمز عبور
        """
        if not phone_number:
            raise ValueError('شماره موبایل الزامی است.')
        phone_number = self.normalize_email(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        ایجاد یک سوپر یوزر با شماره موبایل و رمز عبور
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('subscription_type', 'semi_annual')  # سوپر یوزر به صورت پیش‌فرض دارای اشتراک مادام‌العمر است

        if extra_fields.get('is_staff') is not True:
            raise ValueError('سوپر یوزر باید دارای is_staff=True باشد.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('سوپر یوزر باید دارای is_superuser=True باشد.')

        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(regex=r'^09\d{9}$', message="شماره موبایل باید به فرمت صحیح وارد شود.")
    phone_number = models.CharField(validators=[phone_regex], max_length=11, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    subscription_type = models.CharField(max_length=50, choices=[
        ('free', 'رایگان'),
        ('monthly', 'یک ماهه'),
        ('quarterly', 'سه ماهه'),
        ('semi_annual', 'شش ماهه'),
    ], default='free')
    subscription_expiration = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    otp = models.CharField(max_length=6, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

class SubscriptionPackage(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()  # قیمت به تومان
    duration_in_months = models.IntegerField()
    max_surveys_per_month = models.IntegerField(null=True, blank=True)  # تعداد نظرسنجی مجاز در هر ماه

    def __str__(self):
        return self.name

class Survey(models.Model):
    creator = models.ForeignKey(User, related_name='surveys', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    creation_date = models.DateField(auto_now_add=True)
    editable_until = models.DateField()
    is_active = models.BooleanField(default=True)
    background = models.ImageField(upload_to='backgrounds/', null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    def is_editable(self):
        """
        کاربران فقط می‌توانند نظرسنجی‌ها را تا یک ماه ویرایش کنند
        """
        return self.editable_until >= timezone.now().date()

    def __str__(self):
        return self.title

class Question(models.Model):
    SURVEY_TYPE_CHOICES = [
        ('word_cloud', 'ابر کلمات'),
        ('poll', 'نظرسنجی چند گزینه‌ای'),
        ('scale', 'مقیاس‌بندی'),
        ('ranking', 'رتبه‌بندی'),
        ('video', 'ویدیو'),
    ]
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=50, choices=SURVEY_TYPE_CHOICES)
    options = models.TextField(blank=True, null=True)  # ذخیره گزینه‌ها به صورت JSON برای سوالات چند گزینه‌ای

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)

    def __str__(self):
        return self.choice_text

class Response(models.Model):
    question = models.ForeignKey(Question, related_name='responses', on_delete=models.CASCADE)
    participant_id = models.CharField(max_length=255)
    answer_text = models.TextField()
    submitted_choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"پاسخ به {self.question} توسط {self.participant_id}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'پرداخت نشده'),
        ('paid', 'پرداخت شده'),
        ('failed', 'پرداخت ناموفق'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE)
    authority = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'پرداخت {self.id} - {self.user.phone_number} - {self.status}'

class Page(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
