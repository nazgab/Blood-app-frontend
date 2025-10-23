from rest_framework import generics, permissions
from .legacy_models import LegacyUser, Center, Donation, Bonus
from .legacy_serializers import (LegacyUserSerializer, CenterSerializer,
                                 DonationSerializer, BonusSerializer)

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
