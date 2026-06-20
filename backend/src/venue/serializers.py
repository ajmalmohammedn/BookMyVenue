from rest_framework import serializers
from django.utils.text import slugify
from .models import Venue, VenueImage, VenueAvailability, Amenity, VenueCategory, VenueAmenity



class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Amenity
        fields = ["id", "name", "icon"]



class VenueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = VenueCategory
        fields = ["id", "name", "slug", "icon"]



class VenueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VenueImage
        fields = ["id", "image", "is_primary", "order"]


class VenueAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model  = VenueAvailability
        fields = ["id", "day_of_week", "day_name", "open_time", "close_time", "is_closed"]

    def validate(self, attrs):
        if not attrs.get("is_closed"):
            if attrs.get("open_time") and attrs.get("close_time"):
                if attrs["open_time"] >= attrs["close_time"]:
                    raise serializers.ValidationError({
                        "close_time": "Close time must be after open time."
                    })
        return attrs



class VenueListSerializer(serializers.ModelSerializer):
    category     = VenueCategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    owner_name   = serializers.CharField(source="owner.full_name", read_only=True)

    class Meta:
        model  = Venue
        fields = [
            "id", "name", "slug", "status",
            "city", "state",
            "price_per_hour", "price_per_day",
            "min_capacity", "max_capacity",
            "category", "primary_image", "owner_name",
            "created_at"
        ]

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True, is_deleted=False).first()
        if not image:
            image = obj.images.filter(is_deleted=False).first()
        if image:
            request = self.context.get("request")
            return request.build_absolute_uri(image.image.url) if request else image.image.url
        return None



class VenueDetailSerializer(serializers.ModelSerializer):
    category     = VenueCategorySerializer(read_only=True)
    amenities    = AmenitySerializer(many=True, read_only=True)
    images       = VenueImageSerializer(many=True, read_only=True)
    availability = VenueAvailabilitySerializer(many=True, read_only=True)
    owner_name   = serializers.CharField(source="owner.full_name", read_only=True)

    class Meta:
        model  = Venue
        fields = [
            "id", "name", "slug", "description", "status",
            "address", "city", "state", "pincode",
            "latitude", "longitude",
            "price_per_hour", "price_per_day",
            "min_capacity", "max_capacity",
            "category", "amenities", "images",
            "availability", "owner_name", "created_at", "updated_at"
        ]



class VenueCreateUpdateSerializer(serializers.ModelSerializer):
    amenity_ids  = serializers.ListField(
        child    = serializers.UUIDField(),
        write_only = True,
        required   = False
    )
    availability = VenueAvailabilitySerializer(many=True, required=False)

    class Meta:
        model  = Venue
        fields = [
            "name", "description", "status", "category",
            "address", "city", "state", "pincode",
            "latitude", "longitude",
            "price_per_hour", "price_per_day",
            "min_capacity", "max_capacity",
            "amenity_ids", "availability"
        ]

    def validate_name(self, value):
        return value.strip()

    def validate(self, attrs):
        min_cap = attrs.get("min_capacity", 1)
        max_cap = attrs.get("max_capacity")
        if max_cap and min_cap > max_cap:
            raise serializers.ValidationError({
                "min_capacity": "Min capacity cannot be greater than max capacity."
            })
        return attrs

    def _generate_unique_slug(self, name, instance=None):
        slug      = slugify(name)
        base_slug = slug
        counter   = 1

        qs = Venue.all_objects.filter(slug=slug)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        while qs.exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            qs = Venue.all_objects.filter(slug=slug)
            if instance:
                qs = qs.exclude(pk=instance.pk)
        return slug

    def _save_availability(self, venue, availability_data):
        # Delete old and recreate (clean approach)
        venue.availability.all().delete()
        for avail in availability_data:
            VenueAvailability.objects.create(venue=venue, **avail)

    def _save_amenities(self, venue, amenity_ids):
        VenueAmenity.objects.filter(venue=venue).delete()
        amenities = Amenity.objects.filter(id__in=amenity_ids)
        for amenity in amenities:
            VenueAmenity.objects.create(venue=venue, amenity=amenity)

    def create(self, validated_data):
        amenity_ids      = validated_data.pop("amenity_ids", [])
        availability_data = validated_data.pop("availability", [])

        validated_data["owner"] = self.context["request"].user
        validated_data["slug"]  = self._generate_unique_slug(validated_data["name"])

        venue = Venue.objects.create(**validated_data)

        self._save_amenities(venue, amenity_ids)
        self._save_availability(venue, availability_data)

        return venue

    def update(self, instance, validated_data):
        amenity_ids       = validated_data.pop("amenity_ids", None)
        availability_data = validated_data.pop("availability", None)

        # Regenerate slug only if name changed
        if "name" in validated_data and validated_data["name"] != instance.name:
            validated_data["slug"] = self._generate_unique_slug(
                validated_data["name"], instance=instance
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if amenity_ids is not None:
            self._save_amenities(instance, amenity_ids)

        if availability_data is not None:
            self._save_availability(instance, availability_data)

        return instance
    

class VenueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueCategory
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name", "icon"]
        read_only_fields = ["id"]


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = "__all__" 

        read_only_fields = [
            "id",
            "owner",
            "slug",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        min_capacity = attrs.get(
            "min_capacity",
            getattr(self.instance, "min_capacity", None),
        )
        max_capacity = attrs.get(
            "max_capacity",
            getattr(self.instance, "max_capacity", None),
        )

        if (
            min_capacity is not None
            and max_capacity is not None
            and min_capacity > max_capacity
        ):
            raise serializers.ValidationError(
                {
                    "max_capacity": (
                        "Maximum capacity must be greater than or equal to "
                        "minimum capacity."
                    )
                }
            )

        return attrs


class VenueAvailabilitySerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(
        source="get_day_of_week_display", read_only=True
    )

    class Meta:
        model = VenueAvailability
        fields = [
            "id",
            "venue",
            "day_of_week",
            "day_of_week_display",
            "open_time",
            "close_time",
            "is_closed",
        ]
        read_only_fields = ["id", "venue"]

    def validate(self, attrs):
        is_closed = attrs.get(
            "is_closed", getattr(self.instance, "is_closed", False)
        )
        open_time = attrs.get(
            "open_time", getattr(self.instance, "open_time", None)
        )
        close_time = attrs.get(
            "close_time", getattr(self.instance, "close_time", None)
        )

        if is_closed:
            if open_time or close_time:
                raise serializers.ValidationError(
                    "A closed day should not have open_time or close_time set."
                )
        else:
            if open_time is None or close_time is None:
                raise serializers.ValidationError(
                    "open_time and close_time are required unless the day is marked closed."
                )
            if open_time >= close_time:
                raise serializers.ValidationError(
                    "close_time must be after open_time."
                )

        return attrs
    
    
class VenueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueImage
        fields = [
            "id",
            "venue",
            "image",
            "is_primary",
            "order",
            "uploaded_at",
        ]
        read_only_fields = ["id", "venue", "uploaded_at"]