from rest_framework.permissions import BasePermission


class IsBookingOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
    

class IsVenueOwnerOfBooking(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.venue.owner_id == request.user.id


class IsBookingOwnerOrVenueOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.user_id == request.user.id
            or obj.venue.owner_id == request.user.id
        )