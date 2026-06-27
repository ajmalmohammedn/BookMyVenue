import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator
from accounts.models import User
from .utils import generate_unique_slug, venue_image_upload_path


class SoftDeleteManager(models.Manager):
    #only return active 
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
   
    def get_queryset(self):
        return super().get_queryset()


class SoftDeleteModel(models.Model):

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects     = SoftDeleteManager()  
    all_objects = AllObjectsManager()  

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])



class VenueCategory(models.Model):
    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, null=True, blank=True)  

    class Meta:
        ordering = ["name"]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self.__class__, self.name, self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


#Facilities
class Amenity(models.Model):
    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name



class Venue(SoftDeleteModel):
    STATUS_CHOICES = (
        ("draft",    "Draft"),      # saved but not published
        ("active",   "Active"),     # visible to customers
        ("inactive", "Inactive"),   # hidden by owner
    )

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="venues")
    category    = models.ForeignKey(VenueCategory, on_delete=models.SET_NULL, null=True, related_name="venues")
    amenities   = models.ManyToManyField(Amenity, related_name="venues")

    # Basic Info
    name        = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # Location
    address     = models.TextField()
    city        = models.CharField(max_length=100)
    state       = models.CharField(max_length=100)
    pincode     = models.CharField(max_length=10)
    latitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Pricing & Capacity
    price_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    price_per_day  = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )
    min_capacity   = models.PositiveIntegerField(default=1)
    max_capacity   = models.PositiveIntegerField()

    # Timestamps
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self.__class__, self.name, self.id)
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.max_capacity < self.min_capacity:
            raise ValidationError("max_capacity must be greater than or equal to min_capacity.")
    def is_open_at(self, dt):
        """
        dt: a timezone-aware datetime.
        Returns True if the venue is open at this specific date and time.
        """
        slot = self.availability_slots.filter(day_of_week=dt.weekday()).first()
        if slot is None or slot.is_closed:
            return False
        return slot.open_time <= dt.time() <= slot.close_time

    def __str__(self):
        owner_email = self.owner.email if self.owner else "---"
        return f"{self.name} — {owner_email}"


class VenueImage(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to=venue_image_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
    )
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-uploaded_at"]

    def clean(self):
        max_size_mb = 5
        if self.image and self.image.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"Image must be under {max_size_mb}MB.")

    def __str__(self):
        return f"Image for {self.venue.name}"


class VenueAmenity(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue   = models.ForeignKey(Venue, on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

    class Meta:
        unique_together     = ("venue", "amenity")
        verbose_name        = _("Venue Amenity")
        verbose_name_plural = _("Venue Amenities")


class VenueAvailability(models.Model):
    DAYS_OF_WEEK = (
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue = models.ForeignKey(
        Venue, on_delete=models.CASCADE, related_name="availability_slots"
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)

    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    is_closed = models.BooleanField(
        default=False,
        help_text=_("Mark this day as fully closed (holiday/off day)."),
    )

    class Meta:
        unique_together = ("venue", "day_of_week")
        verbose_name = _("Venue Availability")
        verbose_name_plural = _("Venue Availabilities")
        ordering = ["day_of_week"]

    def clean(self):
        if self.is_closed:
            if self.open_time or self.close_time:
                raise ValidationError(
                    "A closed day should not have open_time or close_time set."
                )
        else:
            if self.open_time is None or self.close_time is None:
                raise ValidationError(
                    "open_time and close_time are required unless the day is marked closed."
                )
            if self.open_time >= self.close_time:
                raise ValidationError("close_time must be after open_time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.is_closed:
            return f"{self.venue.name} — {self.get_day_of_week_display()} (Closed)"
        return (
            f"{self.venue.name} — {self.get_day_of_week_display()} "
            f"({self.open_time}–{self.close_time})"
        )