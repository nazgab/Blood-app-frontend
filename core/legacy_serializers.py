from rest_framework import serializers
from .legacy_models import LegacyUser, Center, Donation, Bonus

class LegacyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegacyUser
        fields = ["user_id","first_name","last_name","blood_group","iin","age","weight",
                  "city","address","phone","email","created_at"]

class CenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Center
        fields = ["center_id","center_name","address","latitude","longitude","contact"]

class DonationSerializer(serializers.ModelSerializer):
    user = LegacyUserSerializer(read_only=True)
    center = CenterSerializer(read_only=True)
    class Meta:
        model = Donation
        fields = ["donation_id","user","center","donation_date","volume_ml","confirmed"]

class BonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonus
        fields = ["bonus_id","user","points","updated_at"]
