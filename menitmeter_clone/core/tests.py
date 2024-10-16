# core/tests.py

from django.test import TestCase
from .models import User, Survey, Question, Choice, Payment, SubscriptionPackage
from django.urls import reverse

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(phone_number='09123456789', password='password123')
        self.assertEqual(user.phone_number, '09123456789')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.subscription_type, 'free')

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(phone_number='09999999999', password='adminpass')
        self.assertEqual(superuser.phone_number, '09999999999')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

class SurveyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='09123456789', password='password123')

    def test_create_survey(self):
        survey = Survey.objects.create(
            creator=self.user,
            title='نظرسنجی تست',
            description='توضیحات تستی',
            editable_until=timezone.now().date() + timedelta(days=30)
        )
        self.assertEqual(survey.title, 'نظرسنجی تست')
        self.assertTrue(survey.is_editable())

class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number='09123456789', password='password123')
        self.package = SubscriptionPackage.objects.create(
            name='monthly',
            price=200000,
            duration_in_months=1,
            max_surveys_per_month=5
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')

    def test_create_survey_limit(self):
        self.client.login(phone_number='09123456789', password='password123')
        for _ in range(2):
            Survey.objects.create(
                creator=self.user,
                title='نظرسنجی تست',
                description='توضیحات تستی',
                editable_until=timezone.now().date() + timedelta(days=30)
            )
        response = self.client.post(reverse('create_survey'), {
            'title': 'نظرسنجی اضافی',
            'description': 'توضیحات اضافی'
        })
        self.assertContains(response, 'شما به حداکثر تعداد نظرسنجی‌های مجاز در این ماه رسیده‌اید.')
