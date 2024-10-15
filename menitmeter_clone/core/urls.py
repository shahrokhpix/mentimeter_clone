from django.urls import path
from .views import phone_login, verify_otp

urlpatterns = [
    path('login/', phone_login, name='phone_login'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('purchase/<int:package_id>/', purchase_subscription, name='purchase_subscription'),
    path('verify-payment/', verify_payment, name='verify_payment'),
]
