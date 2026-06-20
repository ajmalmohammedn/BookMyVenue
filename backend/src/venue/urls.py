from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers  
from .views import (
    VenueAvailabilityViewSet,
    VenueCategoryViewSet,
    VenueDetailUpdateDeleteView,
    MyVenuesView,
    VenueImageView,
    VenueImageViewSet,
    VenueRestoreView,
    AmenityViewSet,
    VenueViewSet,
)

router = routers.DefaultRouter()
router.register(r"venues", VenueViewSet, basename="venue")
router.register(r"amenities", AmenityViewSet, basename="amenity")
router.register(r"categories", VenueCategoryViewSet, basename="venue-category")

venue_router = routers.NestedDefaultRouter(router, r"venues", lookup="venue")
venue_router.register(
    r"availability", VenueAvailabilityViewSet, basename="venue-availability"
)
venue_router.register(r"images", VenueImageViewSet, basename="venue-image")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(venue_router.urls)),
    #public create
    path("<uuid:pk>/", VenueDetailUpdateDeleteView.as_view(), name="venue-detail"),
    #owner 
    path("my-venues/", MyVenuesView.as_view(), name="my-venues"),
    path("<uuid:pk>/restore/", VenueRestoreView.as_view(), name="venue-restore"),
    #images
    path("<uuid:pk>/images/", VenueImageView.as_view(), name="venue-images"),
    path("<uuid:pk>/images/<uuid:image_id>/", VenueImageView.as_view(), name="venue-image-delete"),

]