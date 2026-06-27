from django.urls import path
from .views import (CheckEmailView, VerifyOTPView, LoginView, CompleteProfileView, RefreshTokenView, SetPasswordView, LogoutView, ResetPasswordView)


urlpatterns = [
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),    
    path('set-password/', SetPasswordView.as_view(), name='set-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
]