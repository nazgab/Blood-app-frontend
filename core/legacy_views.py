from rest_framework import generics, permissions
from .legacy_models import LegacyUser, Center, Donation, Bonus
from .legacy_serializers import (LegacyUserSerializer, CenterSerializer,
                                 DonationSerializer, BonusSerializer)
import csv  
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class LegacyUserListView(generics.ListAPIView):
    queryset = LegacyUser.objects.all()
    serializer_class = LegacyUserSerializer
    permission_classes = [permissions.IsAdminUser]  # или AllowAny для теста

class LegacyUserDetailView(generics.RetrieveAPIView):
    lookup_field = "user_id"
    queryset = LegacyUser.objects.all()
    serializer_class = LegacyUserSerializer
    permission_classes = [permissions.IsAdminUser]

class CenterListView(generics.ListAPIView):
    queryset = Center.objects.all()
    serializer_class = CenterSerializer
    permission_classes = [permissions.AllowAny]

class DonationListByUserView(generics.ListAPIView):
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        uid = self.kwargs["user_id"]
        return Donation.objects.filter(user_id=uid).select_related("user","center")

class BonusByUserView(generics.RetrieveAPIView):
    serializer_class = BonusSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        uid = self.kwargs["user_id"]
        return Bonus.objects.get(user_id=uid)
    
class MedicLegacyUserListView(generics.ListAPIView):
    serializer_class = LegacyUserSerializer
    permission_classes = [permissions.IsAuthenticated]  # только залогиненные

    def get_queryset(self):
        user = self.request.user
        # если хотите — точная проверка роли:
        is_medic = getattr(getattr(user, "profile", None), "role", "") == "medic"
        if not (is_medic or user.is_staff):
            return LegacyUser.objects.none()   # пустой набор для не-медиков
        qs = LegacyUser.objects.all().order_by("-id")
        # применим простые фильтры из query params
        q = self.request.query_params.get("q")
        city = self.request.query_params.get("city")
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(iin__icontains=q) |
                Q(email__icontains=q)
            )
        if city:
            qs = qs.filter(city__iexact=city)
        return qs    
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def medic_export_users_csv(request):
    user = request.user
    is_medic = getattr(getattr(user, "profile", None), "role", "") == "medic"
    if not (is_medic or user.is_staff):
        return Response(status=403)

    qs = LegacyUser.objects.all().order_by("id")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="legacy_users.csv"'

    writer = csv.writer(response)
    writer.writerow(["user_id","first_name","last_name","blood_group","iin","city","phone","email"])
    for u in qs:
        writer.writerow([u.user_id, u.first_name, u.last_name, u.blood_group, u.iin, u.city, u.phone, u.email])
    return response    
