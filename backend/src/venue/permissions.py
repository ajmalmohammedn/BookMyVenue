from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsVenueOwner(BasePermission):
    message = "Only venue owners can perform this action."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.role == "venue_owner")
        )

class IsVenueOwnerObject(BasePermission):
    message = "You do not have permission to modify this venue."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if hasattr(obj, "owner"):
            owner = obj.owner
        elif hasattr(obj, "venue"):
            owner = obj.venue.owner
        else:
            return False  # unrecognized model shape — deny rather than crash

        return bool(request.user.is_staff or owner == request.user)