from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers  import (CheckEmailSerializer, VerifyOTPSerializer, LoginSerializer,
                           UserDetailSerializer, CompleteProfileSerializer)
from .models import User
from .utils import create_otp, send_otp_email, get_latest_otp


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }

class CheckEmailView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CheckEmailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)

            if not user.is_email_verified:

                otp_obj = create_otp(user, otp_type="signup")
                send_otp_email(email, otp_obj.otp, otp_type="signup")

                return Response({
                    "status": "verify_otp",
                    "message": "Email not verified. OTP resent to your email"
                })
            
            return Response({
                "status": "login",
                "message": "Email found. Please enter your password."
            })
        
        except User.DoesNotExist:

            # new user
            user = User.objects.create_user(email=email)
            otp_obj = create_otp(user, otp_type="signup")
            send_otp_email(email, otp_obj.otp, otp_type="signup")

            return Response({
                "status": "signup",
                "message": "OTP sent to your email. Please verify."
            }, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(request.data)
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        otp_type = serializer.validated_data["otp_type"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "error": "No account found with this email"},
                status=status.HTTP_404_NOT_FOUND)
        
        otp_obj = get_latest_otp(user, otp_type=otp_type)

        if not otp_obj:
            return Response(
                {"error": "No active OTP found. Please request a new one"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if otp_obj.is_expired():
            return Response(
                {"error": "OTP has expired. Please request a new one"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if otp_obj.otp != otp:
            return Response(
                {"error": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        otp_obj.is_used = True
        otp_obj.save()

        user.is_email_verified = True
        user.is_active = True
        user.save()

        tokens = get_tokens_for_user(user)

        return Response({
            "status": "verified",
            "message": "Email verified, Please complete your profile.",
            "tokens": tokens,
        })



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found with this email."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not user.is_email_verified:
            return Response(
                {"error": "Please verify your email before loggin in."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not user.check_password(password):
            return Response(
                {"error": "Incorrect password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        tokens = get_tokens_for_user(user)

        return Response({
            "status": "success",
            "token": tokens,
            "user": UserDetailSerializer(user).data
        })


class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompleteProfileSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status":  "success",
                "message": "Profile completed!",
                "user":    UserDetailSerializer(request.user).data,
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)