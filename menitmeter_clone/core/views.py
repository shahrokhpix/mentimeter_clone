# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import PhoneLoginForm, OTPForm, SurveyForm, QuestionForm, ChoiceForm
from .models import User, Survey, Question, Choice, SubscriptionPackage, Payment, Response,Page
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import random
from kavenegar import *
from django.conf import settings
from datetime import timedelta
from django.shortcuts import render, redirect
from phone_login.models import PhoneToken
from django.http import JsonResponse
from .models import User
from random import randint

def send_otp_code(phone_number):
    api = KavenegarAPI(settings.SMS_API_KEY)
    otp = random.randint(100000, 999999)
    params = {'receptor': phone_number, 'message': f'کد تایید شما: {otp}'}
    api.sms_send(params)
    return otp

def login_view(request):
    if request.method == 'POST':
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            otp = send_otp_code(phone_number)
            request.session['phone_number'] = phone_number
            request.session['otp'] = otp
            return redirect('verify_otp')
    else:
        form = PhoneLoginForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def dashboard(request):
    surveys = Survey.objects.filter(creator=request.user)
    return render(request, 'core/dashboard.html', {'surveys': surveys})

@login_required
def create_survey(request):
    user = request.user
    current_month = timezone.now().month
    surveys_this_month = Survey.objects.filter(creator=user, creation_date__month=current_month).count()
    max_surveys = get_max_surveys(user.subscription_type)

    if surveys_this_month >= max_surveys:
        return HttpResponse('شما به حداکثر تعداد نظرسنجی‌های مجاز در این ماه رسیده‌اید')

    if request.method == 'POST':
        form = SurveyForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.creator = user
            survey.editable_until = timezone.now() + timedelta(days=30)
            survey.save()
            return redirect('add_question', survey_id=survey.id)
    else:
        form = SurveyForm(user=user)
    return render(request, 'core/create_survey.html', {'form': form})

@login_required
def add_question(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, creator=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.save()
            if question.question_type in ['poll', 'ranking']:
                return redirect('add_choice', question_id=question.id)
            else:
                return redirect('add_question', survey_id=survey.id)
    else:
        form = QuestionForm()
    return render(request, 'core/add_question.html', {'form': form, 'survey': survey})

@login_required
def add_choice(request, question_id):
    question = get_object_or_404(Question, id=question_id, survey__creator=request.user)
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('add_choice', question_id=question.id)
    else:
        form = ChoiceForm()
    return render(request, 'core/add_choice.html', {'form': form, 'question': question})

def participate_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, is_active=True)
    questions = survey.questions.all()
    if request.method == 'POST':
        participant_id = request.session.session_key or random.randint(100000, 999999)
        for question in questions:
            answer = request.POST.get(str(question.id))
            if answer:
                Response.objects.create(question=question, participant_id=participant_id, answer_text=answer)
        return redirect('survey_result', survey_id=survey.id)
    return render(request, 'core/participate_survey.html', {'survey': survey, 'questions': questions})

def survey_result(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.questions.all()
    return render(request, 'core/survey_result.html', {'survey': survey, 'questions': questions})

def get_max_surveys(subscription_type):
    limits = {
        'free': 2,
        'monthly': 5,
        'quarterly': 10,
        'semi_annual': float('inf'),
    }
    return limits.get(subscription_type, 0)

@login_required
def purchase_subscription(request, package_id):
    package = get_object_or_404(SubscriptionPackage, id=package_id)
    if request.method == 'POST':
        amount = package.price
        description = f'خرید اشتراک {package.name}'
        email = request.user.email
        mobile = request.user.phone_number
        callback_url = request.build_absolute_uri('/verify-payment/')
        zarinpal = PaymentRequest(settings.ZARINPAL_MERCHANT_ID)
        result = zarinpal.request(amount, callback_url, description, email, mobile)
        if result['Status'] == '100':
            authority = result['Authority']
            Payment.objects.create(user=request.user, package=package, authority=authority)
            return redirect(f'https://www.zarinpal.com/pg/StartPay/{authority}')
        else:
            return HttpResponse('خطا در ارتباط با زرین‌پال')
    return render(request, 'core/purchase_subscription.html', {'package': package})

@login_required
def verify_payment(request):
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    payment = get_object_or_404(Payment, authority=authority)
    if status == 'OK':
        zarinpal = PaymentVerification(settings.ZARINPAL_MERCHANT_ID)
        result = zarinpal.verify(payment.package.price, authority)
        if result['Status'] == '100':
            payment.status = 'paid'
            payment.save()
            request.user.subscription_type = payment.package.name
            request.user.subscription_expiration = timezone.now() + timedelta(days=payment.package.duration_in_months * 30)
            request.user.save()
            return HttpResponse('پرداخت با موفقیت انجام شد')
        else:
            return HttpResponse('خطا در تایید پرداخت')
    else:
        return HttpResponse('پرداخت توسط کاربر لغو شد')

def page_view(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    return render(request, 'core/page.html', {'page': page})


# core/views.py



def send_otp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if phone_number:
            token, created = PhoneToken.objects.get_or_create(phone_number=phone_number)
            token.send_otp()
            return JsonResponse({'status': 'OTP sent'})
        return JsonResponse({'error': 'Phone number is required'}, status=400)
    return render(request, 'core/send_otp.html')

# core/views.py

def verify_otp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        otp = request.POST.get('otp')
        user = User.objects.filter(phone_number=phone_number, otp=otp).first()
        if user:
            login(request, user)
            return redirect('dashboard')
        return render(request, 'core/verify_otp.html', {'error': 'Invalid OTP'})
    return render(request, 'core/verify_otp.html')


def request_otp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        user = User.objects.filter(phone_number=phone_number).first()
        if user:
            otp = str(randint(100000, 999999))
            user.otp = otp
            user.save()
            # ارسال OTP با استفاده از یک سامانه پیامکی مانند KaveNegar
            send_otp(phone_number, otp)
            return redirect('verify_otp')
    return render(request, 'core/request_otp.html')
