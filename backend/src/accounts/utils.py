import secrets
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta



def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def create_otp(user, otp_type="signup"):
    from .models import OTPVerification

    # Rate limit: max 5 OTPs per 10 minutes
    recent_count = OTPVerification.objects.filter(
        user=user,
        otp_type=otp_type,
        created_at__gte=timezone.now() - timedelta(minutes=10),
    ).count()

    if recent_count >= OTPVerification.MAX_RESEND_COUNT:
        raise Exception("Too many OTP requests. Please try again later.")

    # # Invalidate all previous unused OTPs of same type
    # OTPVerification.objects.filter(
    #     user = user,
    #     otp_type = otp_type,
    #     is_used = False
    # ).update(is_used = True)

    otp = OTPVerification.objects.create(
        user = user,
        otp = generate_otp(),
        otp_type = otp_type,
        expires_at = timezone.now() + timedelta(minutes=OTPVerification.OTP_EXPIRY_MINUTES),
    )

    return otp


def send_otp_email(email, otp, otp_type="signup"):
    from .models import OTPVerification

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

        This OTP is valid for {OTPVerification.OTP_EXPIRY_MINUTES} minutes.
        Do not share this with anyone.

        Thanks,
        BookMyVenue Team """,


        "password_reset": f"""

        Hi,

        You requested to reset your BookMyVenue password.

        Your OTP is:

        {otp}

        This OTP is valid for {OTPVerification.OTP_EXPIRY_MINUTES} minutes.
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

