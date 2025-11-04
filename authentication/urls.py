from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('verify/', views.email_verification, name="email_verification"),
    path('verify/resend/', views.resend_otp, name='resend_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password/verify/', views.reset_password_verify, name='reset_password_verify'),
    path('reset-password/resend-otp/', views.resend_reset_otp, name='resend_reset_otp'),
]

