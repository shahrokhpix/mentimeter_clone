# core/forms.py

from django import forms
from .models import Survey, Question, Choice
from django.contrib.auth.forms import UserCreationForm
from .models import User

class PhoneLoginForm(forms.Form):
    phone_number = forms.CharField(label='شماره موبایل', max_length=15)

class OTPForm(forms.Form):
    otp = forms.CharField(label='کد تایید', max_length=6)

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SurveyForm, self).__init__(*args, **kwargs)
        if user.subscription_type != 'free':
            self.fields['logo'] = forms.ImageField(required=False)
            self.fields['background'] = forms.ImageField(required=False)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
