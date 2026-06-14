from django.urls import path
from .views import (CheckEmailView, VerifyOTPView)


urlpatterns = [
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
]