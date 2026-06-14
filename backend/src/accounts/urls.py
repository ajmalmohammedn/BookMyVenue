from django.urls import path
from .views import (CheckEmailView, VerifyOTPView, LoginView, CompleteProfileView)


urlpatterns = [
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),    

]