from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Venue, VenueImage
from .permissions import IsVenueOwner, IsVenueOwnerObject
from .serializers import (
    VenueListSerializer,
    VenueDetailSerializer,
    VenueCreateUpdateSerializer,
    VenueImageSerializer,
)


def get_owner_venue(pk, user):
    return get_object_or_404(Venue, pk=pk, owner=user, is_deleted=False)


class VenueListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsVenueOwner()]
        return [AllowAny()]

    def get(self, request):
        venues = Venue.objects.filter(status="active").select_related(
            "owner", "category"
        ).prefetch_related("images")

        # Filters
        city     = request.query_params.get("city")
        state    = request.query_params.get("state")
        category = request.query_params.get("category")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        capacity  = request.query_params.get("capacity")

        if city:
            venues = venues.filter(city__icontains=city)
        if state:
            venues = venues.filter(state__icontains=state)
        if category:
            venues = venues.filter(category__slug=category)
        if min_price:
            venues = venues.filter(price_per_hour__gte=min_price)
        if max_price:
            venues = venues.filter(price_per_hour__lte=max_price)
        if capacity:
            venues = venues.filter(
                min_capacity__lte=capacity,
                max_capacity__gte=capacity
            )

        serializer = VenueListSerializer(venues, many=True, context={"request": request})
        return Response({
            "count":  venues.count(),
            "venues": serializer.data
        })

    def post(self, request):
        serializer = VenueCreateUpdateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            venue = serializer.save()
            return Response(
                VenueDetailSerializer(venue, context={"request": request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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