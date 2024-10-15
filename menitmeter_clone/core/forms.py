from django import forms
from models import Survey

class PhoneLoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15)

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'logo']  # در پلن‌های پولی قابل شخصی‌سازی است