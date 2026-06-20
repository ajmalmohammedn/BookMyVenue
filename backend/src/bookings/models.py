import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from venue.models import Venue


class Booking(models.Model):

    STATUS_PENDING   = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_PENDING,   "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_COMPLETED, "Completed"),
    ]

    ACTIVE_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    event_type = models.CharField(max_length=100)
    guest_count = models.PositiveIntegerField()
    special_request  = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["venue", "booking_date", "status"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.venue.name} - {self.booking_date} ({self.status})"
        
    def clean(self):
        errors = {}

        if self.venue_id and self.venue.status != "active":
            errors["venue"] = "This venue is not currently accepting bookings."

        if self.venue_id and self.guest_count and self.venue.max_capacity:
            if self.guest_count > self.venue.max_capacity:
                errors["guest_count"] = (
                    f"Guest count exceeds venue capacity "
                    f"({self.venue.max_capacity} max).")

        if self.venue_id and self.booking_date:
            clashing = Booking.objects.filter(
                venue=self.venue,
                booking_date=self.booking_date,
                status__in=self.ACTIVE_STATUSES,
            ).exclude(pk=self.pk)

            if clashing.exists():
                errors["booking_date"] = (
                    "This venue is already booked (or pending) for the selected date.")

        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    


                