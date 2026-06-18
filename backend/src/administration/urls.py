from django.urls import path
from .views import (
    AdminDashboardView,
    AdminUserListView,
    AdminUserDetailView,
    AdminUserActionView,
    AdminVenueListView,
    AdminVenueDetailView,
    AdminVenueActionView,
    AdminVenueOverviewView,
    AdminUserOverviewView,
)

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),

    path("users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("users/<uuid:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("users/<uuid:pk>/action/", AdminUserActionView.as_view(), name="admin-user-action"),

    path("venues/", AdminVenueListView.as_view(), name="admin-venue-list"),
    path("venues/<uuid:pk>/", AdminVenueDetailView.as_view(), name="admin-venue-detail"),
    path("venues/<uuid:pk>/action/", AdminVenueActionView.as_view(), name="admin-venue-action"),

    path("overview/venues/", AdminVenueOverviewView.as_view(), name="admin-venue-overview"),
    path("overview/users/", AdminUserOverviewView.as_view(), name="admin-user-overview"),
]