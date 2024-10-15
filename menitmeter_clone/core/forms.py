from django import forms

class PhoneLoginForm(forms.Form):
    phone_number = forms.CharField(max_length=15)
