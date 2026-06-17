from django.urls import path
from .views import (
    VenueListCreateView,
    VenueDetailUpdateDeleteView,
    MyVenuesView,
    VenueImageView,
    VenueRestoreView,
)

urlpatterns = [
    #public create
    path("", VenueListCreateView.as_view(), name="venue-list-create"),
    path("<uuid:pk>/", VenueDetailUpdateDeleteView.as_view(), name="venue-detail"),
    #owner 
    path("my-venues/", MyVenuesView.as_view(), name="my-venues"),
    path("<uuid:pk>/restore/", VenueRestoreView.as_view(), name="venue-restore"),
    #images
    path("<uuid:pk>/images/", VenueImageView.as_view(), name="venue-images"),
    path("<uuid:pk>/images/<uuid:image_id>/", VenueImageView.as_view(), name="venue-image-delete"),
]