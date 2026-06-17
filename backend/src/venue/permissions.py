from rest_framework.permissions import BasePermission


class IsVenueOwner(BasePermission):
    message = "Only venue owners can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "venue_owner"
        )


class IsVenueOwnerObject(BasePermission):
    message = "You do not have permission to modify this venue."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user