from django.shortcuts import render, redirect
from .forms import PhoneLoginForm
from kavenegar import KavenegarAPI
from django.conf import settings
import random
from django.http import HttpResponse
from models import Survey
def send_otp(phone_number):
    api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
    otp = random.randint(1000, 9999)
    params = {'receptor': phone_number, 'message': f'Your OTP code is: {otp}'}
    api.sms_send(params)
    return otp

def phone_login(request):
    if request.method == 'POST':
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            otp = send_otp(phone_number)
            request.session['phone_number'] = phone_number
            request.session['otp'] = otp
            return redirect('verify_otp')
    else:
        form = PhoneLoginForm()
    return render(request, 'core/phone_login.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == str(request.session.get('otp')):
            # کاربر را لاگین کن یا کاربر جدیدی ایجاد کن
            phone_number = request.session.get('phone_number')
            user, created = User.objects.get_or_create(phone_number=phone_number)
            login(request, user)
            return HttpResponse('Login successful!')
        else:
            return HttpResponse('Invalid OTP, try again.')
    return render(request, 'core/verify_otp.html')

def survey_detail(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    if survey.creator.subscription_type != 'free':
        # اجازه به شخصی‌سازی بک‌گراند و لوگو
        return render(request, 'core/survey_detail.html', {'survey': survey, 'customizable': True})
    else:
        return render(request, 'core/survey_detail.html', {'survey': survey, 'customizable': False})