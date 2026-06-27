from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView, PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Amenity, Venue, VenueAvailability, VenueCategory, VenueImage
from .permissions import IsVenueOwner, IsVenueOwnerObject
from .serializers import (
    AmenitySerializer,
    VenueAvailabilitySerializer,
    VenueCategorySerializer,
    VenueListSerializer,
    VenueDetailSerializer,
    VenueCreateUpdateSerializer,
    VenueImageSerializer,
    VenueSerializer,
)

def get_owner_venue(pk, user):
    return get_object_or_404(Venue, pk=pk, owner=user, is_deleted=False)



class VenueDetailUpdateDeleteView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsVenueOwner()]

    def get_object(self, pk, user=None):
        if user:
            return get_owner_venue(pk, user)
        return get_object_or_404(Venue, pk=pk, is_deleted=False, status="active")

    def get(self, request, pk):
        venue      = self.get_object(pk)
        serializer = VenueDetailSerializer(venue, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        venue      = self.get_object(pk, user=request.user)
        serializer = VenueCreateUpdateSerializer(
            venue, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            venue = serializer.save()
            return Response(VenueDetailSerializer(venue, context={"request": request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        venue      = self.get_object(pk, user=request.user)
        serializer = VenueCreateUpdateSerializer(
            venue, data=request.data,
            partial=True, context={"request": request}
        )
        if serializer.is_valid():
            venue = serializer.save()
            return Response(VenueDetailSerializer(venue, context={"request": request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        venue = self.get_object(pk, user=request.user)
        venue.soft_delete()
        return Response(
            {"message": "Venue deleted successfully."},
            status=status.HTTP_200_OK
        )



class MyVenuesView(APIView):
    permission_classes = [IsAuthenticated, IsVenueOwner]

    def get(self, request):
        venues = Venue.objects.filter(
            owner=request.user, is_deleted=False
        ).select_related("category").prefetch_related("images")

        serializer = VenueListSerializer(venues, many=True, context={"request": request})
        return Response({
            "count":  venues.count(),
            "venues": serializer.data
        })



class VenueImageView(APIView):
    permission_classes = [IsAuthenticated, IsVenueOwner]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request, pk):
        venue  = get_owner_venue(pk, request.user)
        images = request.FILES.getlist("images")

        if not images:
            return Response(
                {"error": "No images provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(images) > 10:
            return Response(
                {"error": "Maximum 10 images allowed per venue."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        for index, image in enumerate(images):
            # First image = primary if no primary exists
            is_primary = (
                index == 0 and
                not venue.images.filter(is_primary=True, is_deleted=False).exists()
            )
            img = VenueImage.objects.create(
                venue      = venue,
                image      = image,
                is_primary = is_primary,
                order      = index,
            )
            created.append(img)

        serializer = VenueImageSerializer(created, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk, image_id):
        venue = get_owner_venue(pk, request.user)
        image = get_object_or_404(VenueImage, pk=image_id, venue=venue, is_deleted=False)
        image.soft_delete()  

        # if primary image delete , assign next image 
        if image.is_primary:
            next_image = venue.images.filter(is_deleted=False).first()
            if next_image:
                next_image.is_primary = True
                next_image.save()

        return Response(
            {"message": "Image deleted successfully."},
            status=status.HTTP_200_OK
        )



class VenueRestoreView(APIView):
    permission_classes = [IsAuthenticated, IsVenueOwner]

    def post(self, request, pk):
        venue = get_object_or_404(
            Venue, pk=pk, owner=request.user, is_deleted=True
        )
        venue.restore()
        return Response(
            {"message": "Venue restored successfully."},
            status=status.HTTP_200_OK
        )
    
class VenueCategoryViewSet(viewsets.ModelViewSet):
    queryset = VenueCategory.objects.all()
    serializer_class = VenueCategorySerializer
    permission_classes = [IsAuthenticated, IsVenueOwner]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset
    

class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticated, IsVenueOwner, IsVenueOwnerObject]

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset
    

class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()  # fallback only; get_queryset() does the real work
    serializer_class = VenueSerializer
    permission_classes = [IsVenueOwner, IsVenueOwnerObject]
    lookup_field = "slug"

    def get_queryset(self):
        user = self.request.user
        queryset = Venue.objects.select_related("category", "owner").prefetch_related("amenities")

        if user.is_authenticated and user.is_staff:
            return queryset

        if user.is_authenticated:
            return queryset.filter(Q(status="active") | Q(owner=user))

        return queryset.filter(status="active")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class VenueAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = VenueAvailabilitySerializer
    permission_classes = [IsVenueOwner, IsVenueOwnerObject]

    def get_venue(self):
        return get_object_or_404(Venue, slug=self.kwargs["venue_slug"])

    def get_queryset(self):
        venue = self.get_venue()
        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return VenueAvailability.objects.filter(venue=venue)

        if user.is_authenticated and venue.owner_id == user.id:
            return VenueAvailability.objects.filter(venue=venue)

        if venue.status == "active":
            return VenueAvailability.objects.filter(venue=venue)

        # venue is draft/inactive and requester is neither staff nor the owner
        return VenueAvailability.objects.none()

    def perform_create(self, serializer):
        venue = self.get_venue()
        if not (self.request.user.is_staff or venue.owner_id == self.request.user.id):
            raise PermissionDenied("You do not own this venue.")
        serializer.save(venue=venue)


class VenueImageViewSet(viewsets.ModelViewSet):
    serializer_class = VenueImageSerializer
    permission_classes = [IsVenueOwner, IsVenueOwnerObject]

    def get_venue(self):
        return get_object_or_404(Venue, slug=self.kwargs["venue_slug"])

    def get_queryset(self):
        venue = self.get_venue()
        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return VenueImage.objects.filter(venue=venue)

        if user.is_authenticated and venue.owner_id == user.id:
            return VenueImage.objects.filter(venue=venue)

        if venue.status == "active":
            return VenueImage.objects.filter(venue=venue)

        return VenueImage.objects.none()
    
    @action(detail=True, methods=["post"])
    def set_primary(self, request, venue_slug=None, pk=None):
        image = self.get_object()
        image.is_primary = True
        image.save()
        return Response(VenueImageSerializer(image).data)

    def perform_create(self, serializer):
        venue = self.get_venue()
        if not (self.request.user.is_staff or venue.owner_id == self.request.user.id):
            raise PermissionDenied("You do not own this venue.")
        serializer.save(venue=venue)
