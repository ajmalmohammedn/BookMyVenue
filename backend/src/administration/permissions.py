from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Only admin role users can access"""
    message = "You do not have admin privileges."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "admin"
        )