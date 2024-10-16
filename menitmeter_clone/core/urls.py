# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-survey/', views.create_survey, name='create_survey'),
    path('survey/<int:survey_id>/add-question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/add-choice/', views.add_choice, name='add_choice'),
    path('survey/<int:survey_id>/participate/', views.participate_survey, name='participate_survey'),
    path('survey/<int:survey_id>/results/', views.survey_result, name='survey_result'),
    path('purchase/<int:package_id>/', views.purchase_subscription, name='purchase_subscription'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('page/<int:page_id>/', views.page_view, name='page_view'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('request-otp/', views.request_otp, name='request_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]
