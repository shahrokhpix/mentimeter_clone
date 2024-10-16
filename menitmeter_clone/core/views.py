# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import PhoneLoginForm, OTPForm, SurveyForm, QuestionForm, ChoiceForm, ChoiceFormSet
from .models import User, Survey, Question, Choice, SubscriptionPackage, Payment, Response, Page
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import random
from kavenegar import KavenegarAPI, APIException, HTTPException
from django.conf import settings
from datetime import timedelta

def send_otp_code(phone_number):
    """
    ارسال کد OTP به شماره موبایل کاربر با استفاده از کاوه نگار
    """
    api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
    otp = str(random.randint(100000, 999999))
    params = {
        'receptor': phone_number,
        'message': f'کد تایید شما: {otp}'
    }
    try:
        response = api.sms_send(params)
        return otp
    except APIException as e:
        # مدیریت خطاهای API
        print(f"APIException: {e}")
        return None
    except HTTPException as e:
        # مدیریت خطاهای HTTP
        print(f"HTTPException: {e}")
        return None

def login_view(request):
    """
    نمایش فرم ورود با شماره موبایل و ارسال کد OTP
    """
    if request.method == 'POST':
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            otp = send_otp_code(phone_number)
            if otp:
                request.session['phone_number'] = phone_number
                request.session['otp'] = otp
                return redirect('verify_otp')
            else:
                form.add_error(None, 'خطا در ارسال کد تایید. لطفاً دوباره تلاش کنید.')
    else:
        form = PhoneLoginForm()
    return render(request, 'core/login.html', {'form': form})

def verify_otp(request):
    """
    بررسی کد OTP وارد شده توسط کاربر
    """
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            otp_session = request.session.get('otp')
            phone_number = request.session.get('phone_number')
            if otp_input == otp_session:
                user, created = User.objects.get_or_create(phone_number=phone_number)
                login(request, user)
                del request.session['otp']
                return redirect('dashboard')
            else:
                form.add_error('otp', 'کد تایید وارد شده نادرست است.')
    else:
        form = OTPForm()
    return render(request, 'core/verify_otp.html', {'form': form})

@login_required
def dashboard(request):
    """
    نمایش داشبورد کاربر با لیست نظرسنجی‌ها
    """
    surveys = Survey.objects.filter(creator=request.user)
    return render(request, 'core/dashboard.html', {'surveys': surveys})

@login_required
def create_survey(request):
    """
    ایجاد نظرسنجی جدید
    """
    user = request.user
    current_month = timezone.now().month
    current_year = timezone.now().year
    surveys_count = Survey.objects.filter(
        creator=user,
        creation_date__year=current_year,
        creation_date__month=current_month
    ).count()

    max_surveys = get_max_surveys(user.subscription_type)

    if surveys_count >= max_surveys:
        return HttpResponse('شما به حداکثر تعداد نظرسنجی‌های مجاز در این ماه رسیده‌اید.')

    if request.method == 'POST':
        form = SurveyForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.creator = user
            survey.editable_until = timezone.now().date() + timedelta(days=30)
            survey.save()
            return redirect('add_question', survey_id=survey.id)
    else:
        form = SurveyForm(user=user)
    return render(request, 'core/create_survey.html', {'form': form})

@login_required
def add_question(request, survey_id):
    """
    افزودن سوال به نظرسنجی
    """
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
    """
    افزودن گزینه‌ها به سوالات چندگزینه‌ای
    """
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
    choices = question.choices.all()
    return render(request, 'core/add_choice.html', {'form': form, 'question': question, 'choices': choices})

def participate_survey(request, survey_id):
    """
    شرکت در نظرسنجی
    """
    survey = get_object_or_404(Survey, id=survey_id, is_active=True)
    questions = survey.questions.all()
    if request.method == 'POST':
        participant_id = request.session.session_key or str(random.randint(100000, 999999))
        for question in questions:
            answer = request.POST.get(str(question.id))
            if answer:
                # اگر سوال نوع poll یا ranking دارد، انتخاب گزینه است
                if question.question_type in ['poll', 'ranking']:
                    choice = question.choices.filter(id=answer).first()
                    if choice:
                        Response.objects.create(
                            question=question,
                            participant_id=participant_id,
                            submitted_choice=choice
                        )
                else:
                    # سایر نوع سوالات مانند word_cloud و scale
                    Response.objects.create(
                        question=question,
                        participant_id=participant_id,
                        answer_text=answer
                    )
        return redirect('survey_result', survey_id=survey.id)
    return render(request, 'core/participate_survey.html', {'survey': survey, 'questions': questions})

def survey_result(request, survey_id):
    """
    نمایش نتایج نظرسنجی
    """
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.questions.all()
    results = {}
    for question in questions:
        if question.question_type in ['poll', 'ranking']:
            choices = question.choices.annotate(vote_count=models.Count('response'))
            results[question] = choices
        elif question.question_type == 'word_cloud':
            words = Response.objects.filter(question=question).values_list('answer_text', flat=True)
            word_freq = {}
            for word_list in words:
                for word in word_list.split(','):
                    word = word.strip()
                    if word:
                        word_freq[word] = word_freq.get(word, 0) + 1
            results[question] = word_freq
        elif question.question_type == 'scale':
            responses = Response.objects.filter(question=question).values_list('answer_text', flat=True)
            scale_values = [int(response) for response in responses if response.isdigit()]
            average = sum(scale_values) / len(scale_values) if scale_values else 0
            results[question] = average
        elif question.question_type == 'video':
            # برای سوالات ویدیویی، می‌توانید نتایج خاصی را نمایش دهید یا تخلیه کنید
            results[question] = None
    return render(request, 'core/survey_result.html', {'survey': survey, 'results': results})

def get_max_surveys(subscription_type):
    """
    دریافت حداکثر تعداد نظرسنجی‌های مجاز بر اساس نوع اشتراک
    """
    limits = {
        'free': 2,
        'monthly': 5,
        'quarterly': 10,
        'semi_annual': float('inf'),
    }
    return limits.get(subscription_type, 0)

@login_required
def purchase_subscription(request, package_id):
    """
    خرید اشتراک جدید از طریق زرین‌پال
    """
    package = get_object_or_404(SubscriptionPackage, id=package_id)
    if request.method == 'POST':
        amount = package.price * 10  # تبدیل تومان به ریال
        description = f'خرید اشتراک {package.name}'
        mobile = request.user.phone_number
        callback_url = request.build_absolute_uri('/verify-payment/')
        data = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'amount': amount,
            'callback_url': callback_url,
            'description': description,
            'metadata': {'mobile': mobile}
        }
        headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
        try:
            response = requests.post('https://api.zarinpal.com/pg/v4/payment/request.json', json=data, headers=headers)
            response_data = response.json()
            if response_data['data']['code'] == 100:
                authority = response_data['data']['authority']
                Payment.objects.create(user=request.user, package=package, authority=authority)
                return redirect(f'https://www.zarinpal.com/pg/StartPay/{authority}')
            else:
                return HttpResponse(f"خطا در ارتباط با زرین‌پال: {response_data['errors']['message']}")
        except Exception as e:
            return HttpResponse(f"خطا در درخواست پرداخت: {str(e)}")
    return render(request, 'core/purchase_subscription.html', {'package': package})

@login_required
def verify_payment(request):
    """
    تایید پرداخت از زرین‌پال
    """
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    payment = get_object_or_404(Payment, authority=authority)
    if status == 'OK':
        amount = payment.package.price * 10  # تبدیل تومان به ریال
        data = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'authority': authority,
            'amount': amount
        }
        headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
        try:
            response = requests.post('https://api.zarinpal.com/pg/v4/payment/verify.json', json=data, headers=headers)
            response_data = response.json()
            if response_data['data']['code'] == 100:
                payment.status = 'paid'
                payment.save()
                # به‌روزرسانی نوع اشتراک و تاریخ انقضا
                request.user.subscription_type = payment.package.name
                request.user.subscription_expiration = timezone.now().date() + timedelta(days=payment.package.duration_in_months * 30)
                request.user.save()
                return HttpResponse('پرداخت با موفقیت انجام شد و اشتراک شما فعال گردید.')
            else:
                payment.status = 'failed'
                payment.save()
                return HttpResponse('خطا در تایید پرداخت.')
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            return HttpResponse(f"خطا در تایید پرداخت: {str(e)}")
    else:
        payment.status = 'failed'
        payment.save()
        return HttpResponse('پرداخت توسط کاربر لغو شد.')

def page_view(request, page_id):
    """
    نمایش صفحات ایجاد شده توسط ادمین
    """
    page = get_object_or_404(Page, id=page_id)
    return render(request, 'core/page.html', {'page': page})
