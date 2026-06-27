from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Booking
from venue.models import Venue


class BookingListSerializer(serializers.ModelSerializer):

    venue_name = serializers.CharField(source="venue.name", read_only=True)
    venue_slug = serializers.CharField(source="venue.slug", read_only=True)
    user_name  = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model  = Booking
        fields = [
            "id", "venue_name", "venue_slug", "user_name","booking_date", 
            "event_type", "guest_count", "status", "created_at",
        ]


class BookingDetailSerializer(serializers.ModelSerializer):

    venue_name = serializers.CharField(source="venue.name", read_only=True)
    venue_slug = serializers.CharField(source="venue.slug", read_only=True)
    user_name  = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model  = Booking
        fields = [
            "id", "venue", "venue_name", "venue_slug", "user", "user_name", 
            "user_email", "booking_date", "event_type", "guest_count",
            "special_request", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "venue", "status", "created_at", "updated_at"]


class BookingCreateSerializer(serializers.ModelSerializer):

    venue_slug = serializers.SlugField(write_only=True)

    class Meta:
        mode = Booking
        fields = [
            "id", "venue_slug", "booking_date", "event_type",
            "guest_count", "special_request", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]
    
    def validate_venue_slug(self, value):
        try:
            venue = Venue.objects.get(slug=value, is_deleted=False)
        except Venue.DoesNotExist:
            raise serializers.ValidationError("Venue not found")
        
        return venue
    
    def validate_guest_count(self, value):
        if value <= 0:
            raise serializers.ValidationError("Guest count must be at least 1.")
        return value
    
    def validate(self, attrs):
        venue = attrs.get("venue_slug")
        guest_count = attrs.get("guest_count")

        if venue and guest_count and venue.max_capacity:
            if guest_count > venue.max_capacity:
                raise serializers.ValidationError(
                    {
                        "guest_count": f"Guest count exceeds venue capacity ({venue.max_capacity} max)." 
                     }
                )
            
        if venue and venue.status != "active":
            raise serializers.ValidationError({
                "venue_slug": "This venue is not currently accepting bookings."
            })
        
        return attrs
    
    def create(self, validated_data):
        venue = validated_data.pop("venue_slug")
        user = self.context['request'].user()

        booking = Booking(
            user=user,
            venue=venue,
            **validated_data
        )

        try:
            booking.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        
        booking.save()
        return booking