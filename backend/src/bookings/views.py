from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from venue.models import Venue
from .models import Booking
from .serializers import (BookingCreateSerializer, BookingListSerializer,
                          BookingDetailSerializer,)
from .permissions import IsBookingOwner, IsVenueOwnerOfBooking


class CheckAvailabilityView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        venue_slug = request.query_params.get("venue_slug")
        date_str   = request.query_params.get("date")

        if not venue_slug or not date_str:
            return Response(
                {"error": "Both venue_slug and date are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        venue = get_object_or_404(Venue, slug=venue_slug, is_deleted=False)

        is_taken = Booking.objects.filter(
            venue=venue,
            booking_date=booking_date,
            status__in=Booking.ACTIVE_STATUSES,
        ).exists()

        available = venue.status == "active" and not is_taken

        return Response({"available": available})



class BookingCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            booking = serializer.save()
            return Response( BookingDetailSerializer(booking).data,
                status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyBookingsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(
            user=request.user).select_related("venue", "user")

        serializer = BookingListSerializer(bookings, many=True)

        return Response({
            "count":    bookings.count(),
            "bookings": serializer.data,
        })

class BookingDetailView(APIView):

    permission_classes = [IsAuthenticated, IsBookingOwner]

    def get_object(self, pk):
        booking = get_object_or_404(
            Booking.objects.select_related("venue", "user"), pk=pk
        )
        self.check_object_permissions(self.request, booking)

        return booking

    def get(self, request, pk):
        booking = self.get_object(pk)
        return Response(BookingDetailSerializer(booking).data)


class BookingCancelView(APIView):

    permission_classes = [IsAuthenticated, IsBookingOwner]

    def post(self, request, pk):

        booking = get_object_or_404(Booking, pk=pk)

        self.check_object_permissions(request, booking)

        if booking.status not in Booking.ACTIVE_STATUSES:

            return Response(
                {"error": f"Booking is already {booking.status} and cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.STATUS_CANCELLED
        booking.save()

        return Response(BookingDetailSerializer(booking).data)
    

class OwnerBookingListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(
            venue__owner=request.user).select_related("venue", "user")

        serializer = BookingListSerializer(bookings, many=True)

        return Response({
            "count":    bookings.count(),
            "bookings": serializer.data,
        })


class OwnerBookingDetailView(APIView):

    permission_classes = [IsAuthenticated, IsVenueOwnerOfBooking]

    def get_object(self, pk, request):

        booking = get_object_or_404(
            Booking.objects.select_related("venue", "user"), pk=pk
        )

        self.check_object_permissions(request, booking)

        return booking

    def get(self, request, pk):
        booking = self.get_object(pk, request)
        return Response(BookingDetailSerializer(booking).data)
    

class OwnerBookingConfirmView(APIView):

    permission_classes = [IsAuthenticated, IsVenueOwnerOfBooking]

    def post(self, request, pk):

        booking = get_object_or_404(Booking, pk=pk)

        self.check_object_permissions(request, booking)

        if booking.status != Booking.STATUS_PENDING:

            return Response(
                {"error": f"Only pending bookings can be confirmed (current: {booking.status})."},
                status=status.HTTP_400_BAD_REQUEST,
            )


        booking.status = Booking.STATUS_CONFIRMED
        booking.save()

        return Response(BookingDetailSerializer(booking).data)
    

class OwnerBookingRejectView(APIView):

    permission_classes = [IsAuthenticated, IsVenueOwnerOfBooking]

    def post(self, request, pk):

        booking = get_object_or_404(Booking, pk=pk)

        self.check_object_permissions(request, booking)

        if booking.status != Booking.STATUS_PENDING:
            return Response(
                {"error": f"Only pending bookings can be rejected (current: {booking.status})."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.STATUS_CANCELLED
        booking.save()
        
        return Response(BookingDetailSerializer(booking).data)