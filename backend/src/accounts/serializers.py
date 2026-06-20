from rest_framework import serializers
from .models import User, VenueOwnerProfile
from django.contrib.auth.password_validation import validate_password


class BaseEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()


class CheckEmailSerializer(BaseEmailSerializer):
    pass


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


class UserDetailSerializer(serializers.ModelSerializer):
    is_profile_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "role", "full_name", "phone_number","city", "state", 
            "profile_photo","is_email_verified", "is_profile_complete","date_joined"
        ]


class CompleteProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = ["full_name", "phone_number", "city", "state", "role", "profile_photo"]

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters.")
        return value

    def validate_phone_number(self, value):
        if not value.startswith("+"):
            raise serializers.ValidationError("Phone must start with + (e.g. +919876543210).")
        return value

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if instance.role == "venue_owner":
            VenueOwnerProfile.objects.get_or_create(user=instance)

        return instance
    
class SetPasswordSerializer(serializers.Serializer):
    password         = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def save(self, **kwargs):
        user = kwargs["user"]
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])