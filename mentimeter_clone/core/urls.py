# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('create-survey/', views.create_survey, name='create_survey'),
    path('add-question/<int:survey_id>/', views.add_question, name='add_question'),
    path('add-choice/<int:question_id>/', views.add_choice, name='add_choice'),
    path('survey/<int:survey_id>/participate/', views.participate_survey, name='participate_survey'),
    path('survey/<int:survey_id>/results/', views.survey_result, name='survey_result'),
    path('purchase-subscription/<int:package_id>/', views.purchase_subscription, name='purchase_subscription'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('page/<int:page_id>/', views.page_view, name='page_view'),
]
