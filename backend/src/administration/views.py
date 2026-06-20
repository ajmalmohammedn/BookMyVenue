from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from venue.models import Venue, VenueCategory
from .permissions import IsAdminUser
from .serializers import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    AdminUserStatusSerializer,
    AdminVenueCategorySerializer,
    AdminVenueListSerializer,
    AdminVenueDetailSerializer,
    AdminVenueActionSerializer,
)



def admin_permissions():
    return [IsAuthenticated(), IsAdminUser()]


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        now        = timezone.now()
        last_30    = now - timedelta(days=30)
        last_7     = now - timedelta(days=7)

        
        total_users         = User.objects.filter(role__in=["customer", "venue_owner"]).count()
        total_customers     = User.objects.filter(role="customer").count()
        total_venue_owners  = User.objects.filter(role="venue_owner").count()
        new_users_30        = User.objects.filter(date_joined__gte=last_30).count()
        new_users_7         = User.objects.filter(date_joined__gte=last_7).count()
        banned_users        = User.objects.filter(is_active=False).count()
        unverified_users    = User.objects.filter(is_email_verified=False).count()

        
        total_venues        = Venue.all_objects.count()
        active_venues       = Venue.objects.filter(status="active").count()
        draft_venues        = Venue.objects.filter(status="draft").count()
        inactive_venues     = Venue.objects.filter(status="inactive").count()
        deleted_venues      = Venue.all_objects.filter(is_deleted=True).count()
        new_venues_30       = Venue.all_objects.filter(created_at__gte=last_30).count()

        return Response({
            "users": {
                "total":          total_users,
                "customers":      total_customers,
                "venue_owners":   total_venue_owners,
                "new_last_7days": new_users_7,
                "new_last_30days":new_users_30,
                "banned":         banned_users,
                "unverified":     unverified_users,
            },
            "venues": {
                "total":          total_venues,
                "active":         active_venues,
                "draft":          draft_venues,
                "inactive":       inactive_venues,
                "deleted":        deleted_venues,
                "new_last_30days":new_venues_30,
            },
        })


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.exclude(role="admin").order_by("-date_joined")

        # Filters
        role       = request.query_params.get("role")
        is_active  = request.query_params.get("is_active")
        verified   = request.query_params.get("verified")
        search     = request.query_params.get("search")

        if role:
            users = users.filter(role=role)
        if is_active is not None:
            users = users.filter(is_active=is_active.lower() == "true")
        if verified is not None:
            users = users.filter(is_email_verified=verified.lower() == "true")
        if search:
            users = users.filter(
                Q(email__icontains=search)     |
                Q(full_name__icontains=search) |
                Q(phone_number__icontains=search)
            )

        serializer = AdminUserListSerializer(users, many=True)
        return Response({
            "count": users.count(),
            "users": serializer.data
        })



class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        user       = self.get_object(pk)
        serializer = AdminUserDetailSerializer(user, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, pk):
        user = self.get_object(pk)

        if user.role == "admin":
            return Response(
                {"error": "Cannot delete admin users."},
                status=status.HTTP_403_FORBIDDEN
            )

        email = user.email
        user.delete()  
        return Response(
            {"message": f"User {email} permanently deleted."},
            status=status.HTTP_200_OK
        )


class AdminUserActionView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        user       = get_object_or_404(User, pk=pk)
        serializer = AdminUserStatusSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data["action"]

        if user.role == "admin":
            return Response(
                {"error": "Cannot perform actions on admin users."},
                status=status.HTTP_403_FORBIDDEN
            )

        if action == "ban":
            if not user.is_active:
                return Response({"error": "User is already banned."}, status=400)
            user.is_active = False
            user.save()
            return Response({"message": f"{user.email} has been banned."})

        elif action == "unban":
            if user.is_active:
                return Response({"error": "User is not banned."}, status=400)
            user.is_active = True
            user.save()
            return Response({"message": f"{user.email} has been unbanned."})

        elif action == "verify_email":
            if user.is_email_verified:
                return Response({"error": "Email is already verified."}, status=400)
            user.is_email_verified = True
            user.is_active         = True
            user.save()
            return Response({"message": f"{user.email} email verified by admin."})



class AdminVenueListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        venues = Venue.all_objects.select_related(
            "owner", "category"
        ).prefetch_related("images").order_by("-created_at")

        # Filters
        status_filter = request.query_params.get("status")
        is_deleted    = request.query_params.get("is_deleted")
        city          = request.query_params.get("city")
        search        = request.query_params.get("search")
        owner_email   = request.query_params.get("owner_email")

        if status_filter:
            venues = venues.filter(status=status_filter)
        if is_deleted is not None:
            venues = venues.filter(is_deleted=is_deleted.lower() == "true")
        if city:
            venues = venues.filter(city__icontains=city)
        if search:
            venues = venues.filter(
                Q(name__icontains=search) |
                Q(owner__email__icontains=search) |
                Q(city__icontains=search)
            )
        if owner_email:
            venues = venues.filter(owner__email__icontains=owner_email)

        serializer = AdminVenueListSerializer(venues, many=True, context={"request": request})
        return Response({
            "count":  venues.count(),
            "venues": serializer.data
        })



class AdminVenueDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        venue      = get_object_or_404(Venue.all_objects, pk=pk)
        serializer = AdminVenueDetailSerializer(venue, context={"request": request})
        return Response(serializer.data)


class AdminVenueActionView(APIView):
    """Approve / Reject / Restore / Deactivate venue"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        venue      = get_object_or_404(Venue.all_objects, pk=pk)
        serializer = AdminVenueActionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        action = serializer.validated_data["action"]

        if action == "approve":
            if venue.is_deleted:
                return Response({"error": "Cannot approve a deleted venue."}, status=400)
            venue.status = "active"
            venue.save()
            return Response({"message": f"Venue '{venue.name}' approved and set to active."})

        elif action == "reject":
            if venue.is_deleted:
                return Response({"error": "Venue is already deleted."}, status=400)
            venue.status = "inactive"
            venue.save()
            return Response({"message": f"Venue '{venue.name}' rejected and set to inactive."})

        elif action == "deactivate":
            if venue.status == "inactive":
                return Response({"error": "Venue is already inactive."}, status=400)
            venue.status = "inactive"
            venue.save()
            return Response({"message": f"Venue '{venue.name}' has been deactivated."})

        elif action == "restore":
            if not venue.is_deleted:
                return Response({"error": "Venue is not deleted."}, status=400)
            venue.restore()
            return Response({"message": f"Venue '{venue.name}' has been restored."})



class AdminVenueOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        
        by_status = (
            Venue.all_objects
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        by_city = (
            Venue.objects
            .values("city")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        by_category = (
            Venue.objects
            .values("category__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        recently_deleted = Venue.all_objects.filter(
            is_deleted=True
        ).order_by("-deleted_at")[:5]

        return Response({
            "by_status":        list(by_status),
            "by_city":          list(by_city),
            "by_category":      list(by_category),
            "recently_deleted": AdminVenueListSerializer(
                recently_deleted, many=True, context={"request": request}
            ).data,
        })



class AdminUserOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        now     = timezone.now()
        last_30 = now - timedelta(days=30)

       
        new_users_daily = (
            User.objects
            .filter(date_joined__gte=last_30)
            .extra(select={"day": "date(date_joined)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

       
        by_role = (
            User.objects
            .values("role")
            .annotate(count=Count("id"))
            .order_by("role")
        )

        
        by_city = (
            User.objects
            .filter(city__isnull=False)
            .values("city")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        
        recent_users = User.objects.order_by("-date_joined")[:5]

        return Response({
            "new_users_daily": list(new_users_daily),
            "by_role":         list(by_role),
            "by_city":         list(by_city),
            "recent_users":    AdminUserListSerializer(recent_users, many=True).data,
        })
    
class AdminVenueCategoryViewSet(ModelViewSet):
    queryset = VenueCategory.objects.all()
    serializer_class = AdminVenueCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("q")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
    
    