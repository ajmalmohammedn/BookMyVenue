import random
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta


OTP_EXPIRY_MINUTES  = 10
OTP_COOLDOWN_SECONDS = 60
OTP_MAX_RESEND      = 5

def generate_otp():
    return str(random.randint(100000, 999999))


def create_otp(user, otp_type="signup"):
    from .models import OTPVerification

    # Invalidate all previous unused OTPs of same type
    OTPVerification.objects.filter(
        user = user,
        otp_type = otp_type,
        is_used = False
    ).update(is_used = True)

    otp = OTPVerification.objects.create(
        user = user,
        otp = generate_otp(),
        otp_type = otp_type,
        expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )

    return otp


def send_otp_email(email, otp, otp_type="signup"):

    subjects = {
        "signup": "Verify your BookMyVenue account",
        "password_rest": "Reset your BookMyVenue Password",
    }

    messages = {
        "signup": f"""

        Hi,

        Welcome to BookMyVenue.

        Your email verification OTP is:

        {otp}

        This OTP is valid for {OTP_EXPIRY_MINUTES} minutes.
        Do not share this with anyone.

        Thanks,
        BookMyVenue Team """,


        "password_reset": f"""

        Hi,

        You requested to reset your BookMyVenue password.

        Your OTP is:

        {otp}

        This OTP is valid for {OTP_EXPIRY_MINUTES} minutes.
        If you did not request this, ignore this email.

        Thanks,
        BookMyVenue Team """,

    }

    send_mail(
        subject = subjects.get(otp_type, "OTP Verification"),
        message = messages.get(otp_type, f"Your verification OTP is {otp}"),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [email],
        fail_silently = False, 
    )


def get_latest_otp(user, otp_type="signup"):
    from .models import OTPVerification

    return OTPVerification.objects.filter(
        user = user,
        otp_type = otp_type,
        is_used = False
    ).order_by("-created_at").first()

