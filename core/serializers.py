from rest_framework import serializers
from .models import (
    SiteConfig,
    MenuItem,
    HeroBlock,
    Article,
    BloodCenter,
    ContactChannel,
    BonusAccount,
    AboutSection,
    AdminDonation,
)
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator


class SiteConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfig
        fields = [
            "logo",
            "app_link_android",
            "app_link_ios",
            "footer_text_kk",
            "footer_text_ru",
            "footer_text_en",
        ]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["key", "title_kk", "title_ru", "title_en", "href", "order", "visible"]


class HeroBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroBlock
        fields = [
            "title_kk", "title_ru", "title_en",
            "subtitle_kk", "subtitle_ru", "subtitle_en",
            "cta_text_kk", "cta_text_ru", "cta_text_en",
            "cta_url",
        ]


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "slug",
            "title_kk",
            "title_ru",
            "excerpt_kk",
            "excerpt_ru",
            "category",
            "published_at",
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "slug",
            "title_kk",
            "title_ru",
            "excerpt_kk",
            "excerpt_ru",
            "body_kk",
            "body_ru",
            "category",
            "published_at",
            "cover",
        ]


class BloodCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodCenter
        fields = [
            "id",
            "name_kk",
            "name_ru",
            "city",
            "address",
            "phone",
            "hours_kk",
            "hours_ru",
            "geo_lat",
            "geo_lon",
            "is_active",
        ]


class ContactChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactChannel
        fields = ["kind", "value", "label_kk", "label_ru", "order"]


class BonusAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusAccount
        fields = ["balance", "level", "updated_at"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=8)

    def create(self, validated_data):
        email = validated_data["email"].lower()
        user = User.objects.create_user(
            username=email, email=email, password=validated_data["password"]
        )
        return user

    def validate_password(self, value):
        validate_password(value)
        return value


class AboutSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSection
        fields = ['text_kk', 'text_ru', 'text_en']


class DonationSerializer(serializers.Serializer):
    admin_donation_id = serializers.IntegerField()
    user_id = serializers.IntegerField(allow_null=True)
    iin = serializers.CharField(allow_blank=True, allow_null=True)
    blood_group = serializers.CharField(allow_blank=True, allow_null=True)
    center_id = serializers.IntegerField(allow_null=True)
    employee_id = serializers.IntegerField(allow_null=True)
    # если хотите ещё поля из admin_donations — добавьте здесь
