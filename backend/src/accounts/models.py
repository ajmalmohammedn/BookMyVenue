import uuid
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("customer",    "Customer"),
        ("venue_owner", "Venue Owner"),
        ("admin",       "Admin"),
    )

    phone_regex = RegexValidator(
        regex=r'^\+[1-9]\d{7,14}$',
        message="Enter a valid phone number in E.164 format (e.g. +447700900123)."
    )

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email             = models.EmailField(unique=True, db_index=True)
    is_email_verified = models.BooleanField(default=False)
    role              = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    full_name     = models.CharField(max_length=150, null=True, blank=True)
    phone_number  = models.CharField(max_length=15, validators=[phone_regex], null=True, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/", null=True, blank=True)
    city          = models.CharField(max_length=100, null=True, blank=True)
    state         = models.CharField(max_length=100, null=True, blank=True)

    is_active  = models.BooleanField(default=False)  
    is_staff   = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name        = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_profile_complete(self):
        return all([self.full_name, self.phone_number, self.city, self.state])


class OTPVerification(models.Model):
    OTP_TYPE_CHOICES = (
        ("signup",        "Signup Verification"),
        ("password_reset","Password Reset"),
    )

    OTP_EXPIRY_MINUTES = 10
    MAX_FAILED_ATTEMPTS = 5
    MAX_RESEND_COUNT = 5
    RESEND_COOLDOWN_SECONDS = 60

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    otp        = models.CharField(max_length=6)
    otp_type   = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES, default="signup")

    is_used    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    # Track resend attempts
    resend_count    = models.PositiveIntegerField(default=0)
    failed_attempts = models.PositiveIntegerField(default=0)
    last_resent_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name        = _("OTP Verification")
        verbose_name_plural = _("OTP Verifications")
        indexes = [
            models.Index(fields=["user", "otp_type", "is_used"]),
        ]


    def __str__(self):
        return f"{self.user.email} | {self.otp_type} | {'Used' if self.is_used else 'Pending'}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired() and self.failed_attempts < self.MAX_FAILED_ATTEMPTS
    
    def can_resend(self):
        if not self.last_resent_at:
            return True
        cooldown = timedelta(seconds=self.RESEND_COOLDOWN_SECONDS)
        return timezone.now() >= self.last_resent_at + cooldown



class VenueOwnerProfile(models.Model):
    user                = models.OneToOneField(User, on_delete=models.CASCADE, related_name="owner_profile")
    business_name       = models.CharField(max_length=200, null=True, blank=True)
    business_address    = models.TextField(null=True, blank=True)
    gst_number          = models.CharField(max_length=20, blank=True, null=True)
    id_proof_document   = models.FileField(upload_to="id_proofs/", null=True, blank=True)
    is_profile_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name        = _("Venue Owner Profile")
        verbose_name_plural = _("Venue Owner Profiles")

    def __str__(self):
        return self.business_name or f"Owner: {self.user.email}"
    
