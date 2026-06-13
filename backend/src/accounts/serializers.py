from rest_framework import serializers


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


