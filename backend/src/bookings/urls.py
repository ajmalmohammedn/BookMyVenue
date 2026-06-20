from django.urls import path
from. views import (CheckAvailabilityView, BookingCreateView, MyBookingsView,
                    BookingDetailView, BookingCancelView, OwnerBookingListView,
                    OwnerBookingConfirmView, OwnerBookingRejectView, OwnerBookingDetailView,
                    )

urlpatterns = [
    path("check-availability/", CheckAvailabilityView.as_view(), name="booking-check-availability"),
    path("", BookingCreateView.as_view(), name="booking-create"),
    path("my-bookings/", MyBookingsView.as_view(), name="booking-my-bookings"),
    path("<uuid:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path("<uuid:pk>/cancel/", BookingCancelView.as_view(), name="booking-cancel"),
]

owner_urlpatterns = [
    path("", OwnerBookingListView.as_view(), name="owner-booking-list"),
    path("<uuid:pk>/", OwnerBookingDetailView.as_view(), name="owner-booking-detail"),
    path("<uuid:pk>/confirm/", OwnerBookingConfirmView.as_view(), name="owner-booking-confirm"),
    path("<uuid:pk>/reject/", OwnerBookingRejectView.as_view(), name="owner-booking-reject"),
]