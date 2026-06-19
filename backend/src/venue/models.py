import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from src.accounts.models import User


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
        ordering            = ["name"]

    def __str__(self):
        return self.name


#fecilities
class Amenity(models.Model):
    id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering            = ["name"]

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
    amenities   = models.ManyToManyField(Amenity, through="VenueAmenity", related_name="venues")

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
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.owner.email}"


class VenueImage(SoftDeleteModel):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue      = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="images")
    image      = models.ImageField(upload_to="venues/images/")
    is_primary = models.BooleanField(default=False)  # main cover image
    order      = models.PositiveIntegerField(default=0)  # display order
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ["order", "-uploaded_at"]

    def __str__(self):
        return f"Image for {self.venue.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            VenueImage.objects.filter(
                venue=self.venue, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)



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

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue      = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="availability")
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    open_time  = models.TimeField()
    close_time = models.TimeField()
    is_closed  = models.BooleanField(default=False)  # mark holiday/off day

    class Meta:
        unique_together     = ("venue", "day_of_week")
        verbose_name        = _("Venue Availability")
        verbose_name_plural = _("Venue Availabilities")
        ordering            = ["day_of_week"]

    def __str__(self):
        return f"{self.venue.name} — {self.get_day_of_week_display()}"