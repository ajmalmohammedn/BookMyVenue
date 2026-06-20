from rest_framework import serializers
from accounts.models import User
from venue.models import Venue, VenueCategory, VenueImage



class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = [
            "id", "email", "full_name", "phone_number",
            "role", "is_active", "is_email_verified",
            "city", "state", "date_joined"
        ]


class AdminUserDetailSerializer(serializers.ModelSerializer):
    is_profile_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model  = User
        fields = [
            "id", "email", "full_name", "phone_number",
            "role", "is_active", "is_email_verified",
            "is_profile_complete",
            "city", "state",
            "profile_photo", "date_joined", "updated_at"
        ]


class AdminUserStatusSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=[
        "ban", "unban", "verify_email"
    ])
    reason = serializers.CharField(required=False, allow_blank=True)



class AdminVenueListSerializer(serializers.ModelSerializer):
    owner_email    = serializers.EmailField(source="owner.email",     read_only=True)
    owner_name     = serializers.CharField(source="owner.full_name",  read_only=True)
    category_name  = serializers.CharField(source="category.name",    read_only=True)
    image_count    = serializers.SerializerMethodField()

    class Meta:
        model  = Venue
        fields = [
            "id", "name", "slug", "status",
            "city", "state",
            "price_per_hour", "price_per_day",
            "min_capacity", "max_capacity",
            "owner_email", "owner_name", "category_name",
            "image_count", "is_deleted", "deleted_at",
            "created_at", "updated_at"
        ]

    def get_image_count(self, obj):
        return obj.images.filter(is_deleted=False).count()


class AdminVenueDetailSerializer(serializers.ModelSerializer):
    owner         = AdminUserListSerializer(read_only=True)
    images        = serializers.SerializerMethodField()
    amenities     = serializers.StringRelatedField(many=True)
    availability  = serializers.SerializerMethodField()

    class Meta:
        model  = Venue
        fields = [
            "id", "name", "slug", "description", "status",
            "address", "city", "state", "pincode",
            "latitude", "longitude",
            "price_per_hour", "price_per_day",
            "min_capacity", "max_capacity",
            "owner", "amenities", "images", "availability",
            "is_deleted", "deleted_at",
            "created_at", "updated_at"
        ]

    def get_images(self, obj):
        request = self.context.get("request")
        images  = obj.images.filter(is_deleted=False)
        return [
            {
                "id":         str(img.id),
                "url":        request.build_absolute_uri(img.image.url) if request else img.image.url,
                "is_primary": img.is_primary,
                "order":      img.order,
            }
            for img in images
        ]

    def get_availability(self, obj):
        return [
            {
                "day":        avail.get_day_of_week_display(),
                "open_time":  str(avail.open_time),
                "close_time": str(avail.close_time),
                "is_closed":  avail.is_closed,
            }
            for avail in obj.availability.all()
        ]


class AdminVenueActionSerializer(serializers.Serializer):

    action = serializers.ChoiceField(choices=[
        "approve", "reject", "restore", "deactivate"
    ])
    reason = serializers.CharField(required=False, allow_blank=True)


class AdminVenueCategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model  = VenueCategory
        fields = ["id", "name", "slug", "icon"]
        read_only_fields = ["id", "slug"]
