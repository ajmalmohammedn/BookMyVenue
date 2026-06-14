from rest_framework import serializers
from .models import User


class BaseEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()


class CheckEmailSerializer(BaseEmailSerializer):
    pass


class SetPasswordSerializer(BaseEmailSerializer):
    password = serializers.CharField(min_length=8, write_only=True)


class VerifyOTPSerializer(BaseEmailSerializer):
    otp = serializers.CharField(max_length=6, min_length=6)
    otp_type = serializers.ChoiceField(
        choices = ["signup", "password_reset"],
        default = "signup"
    )

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only numbers.")
        return value


class LoginSerializer(BaseEmailSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Password do not match")
        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    is_profile_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "role", "full_name", "phone_number","city", "state", 
            "profile_photo","is_email_verified", "is_profile_complete","date_joined"
        ]
