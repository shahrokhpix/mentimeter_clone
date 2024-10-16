# core/forms.py

from django import forms
from .models import Survey, Question, Choice, User
from django.forms import inlineformset_factory

class PhoneLoginForm(forms.Form):
    phone_number = forms.CharField(
        label='شماره موبایل',
        max_length=11,
        widget=forms.TextInput(attrs={'placeholder': 'مثال: 09123456789'})
    )

class OTPForm(forms.Form):
    otp = forms.CharField(
        label='کد تایید',
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'کد ۶ رقمی'})
    )

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'background', 'logo']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان نظرسنجی'}),
            'description': forms.Textarea(attrs={'placeholder': 'توضیحات نظرسنجی (اختیاری)', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(SurveyForm, self).__init__(*args, **kwargs)
        if user.subscription_type == 'free':
            self.fields.pop('background')
            self.fields.pop('logo')
        else:
            self.fields['background'].required = False
            self.fields['logo'].required = False

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'options']
        widgets = {
            'question_text': forms.TextInput(attrs={'placeholder': 'متن سوال'}),
            'options': forms.Textarea(attrs={'placeholder': 'گزینه‌ها را با کاما جدا کنید', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        options = cleaned_data.get('options')
        if question_type in ['poll', 'ranking'] and not options:
            self.add_error('options', 'برای این نوع سوال باید گزینه‌ها را وارد کنید.')
        return cleaned_data

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
        widgets = {
            'choice_text': forms.TextInput(attrs={'placeholder': 'متن گزینه'}),
        }

# فرم ست برای مدیریت گزینه‌های سوالات چندگزینه‌ای
ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    extra=1,
    can_delete=True
)
