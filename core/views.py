from django.db.models import Q
from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    SiteConfig, MenuItem, HeroBlock, Article, BloodCenter,
    ContactChannel, BonusAccount, AboutSection,
)
from .serializers import (
    SiteConfigSerializer, MenuItemSerializer, HeroBlockSerializer,
    ArticleListSerializer, ArticleDetailSerializer, BloodCenterSerializer,
    ContactChannelSerializer, BonusAccountSerializer, RegisterSerializer,
    AboutSectionSerializer,
)

class AboutSectionView(generics.RetrieveAPIView):
    queryset = AboutSection.objects.all()
    serializer_class = AboutSectionSerializer

    def get_object(self):
        return AboutSection.objects.latest('updated_at')
    
class SiteConfigView(generics.RetrieveAPIView):
    queryset = SiteConfig.objects.all().order_by("-updated_at")
    serializer_class = SiteConfigSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return self.get_queryset().first()


class MenuListView(generics.ListAPIView):
    queryset = MenuItem.objects.filter(visible=True).order_by("order", "id")
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]


class HeroView(generics.RetrieveAPIView):
    queryset = HeroBlock.objects.all().order_by("-updated_at")
    serializer_class = HeroBlockSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return self.get_queryset().first()


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Article.objects.filter(is_published=True)
        category = self.request.query_params.get("category")
        q = self.request.query_params.get("q")
        if category:
            qs = qs.filter(category=category)
        if q:
            qs = qs.filter(
                Q(title_ru__icontains=q) |
                Q(title_kk__icontains=q) |
                Q(excerpt_ru__icontains=q) |
                Q(excerpt_kk__icontains=q)
            )
        return qs


class ArticleDetailView(generics.RetrieveAPIView):
    lookup_field = "slug"
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]


class BloodCenterListView(generics.ListAPIView):
    serializer_class = BloodCenterSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = BloodCenter.objects.filter(is_active=True)
        city = self.request.query_params.get("city")
        if city:
            qs = qs.filter(city__iexact=city)
        return qs


class ContactListView(generics.ListAPIView):
    queryset = ContactChannel.objects.all()
    serializer_class = ContactChannelSerializer
    permission_classes = [permissions.AllowAny]


class BonusMeView(generics.RetrieveAPIView):
    serializer_class = BonusAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = BonusAccount.objects.get_or_create(user=self.request.user)
        return obj


# ======= JWT по email (вариант через SimpleJWT) =======
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Позволяет логиниться по email (подставляя username под капотом)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.EmailField(required=True)
        # username (USERNAME_FIELD) делаем необязательным
        self.fields[self.username_field].required = False

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get("email")
        if email and not attrs.get(self.username_field):
            UserModel = get_user_model()
            try:
                u = UserModel.objects.get(email__iexact=email.strip())
                # SimpleJWT требует USERNAME_FIELD — подставим его
                attrs[self.username_field] = getattr(u, UserModel.USERNAME_FIELD)
            except UserModel.DoesNotExist:
                pass
        return super().validate(attrs)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


# ======= Регистрация (если используешь) =======
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        user = ser.save()
        return Response({"id": user.id, "email": user.email}, status=status.HTTP_201_CREATED)


# ======= Кастомный login по email (без SimpleJWT), тоже рабочий =======
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "email and password required"}, status=400)

        UserModel = get_user_model()
        try:
            user_obj = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=400)

        # аутентифицируем по USERNAME_FIELD
        username_field = UserModel.USERNAME_FIELD
        user = authenticate(request, **{username_field: getattr(user_obj, username_field)}, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=400)
        if not user.is_active:
            return Response({"detail": "User inactive"}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

from types import SimpleNamespace
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Profile

@login_required
def profile_page(request):
    """
    Минимальный view для profile.html:
    - формирует form (как в шаблоне ожидается)
    - получает profile
    - подставляет employee через profile.get_employee() (если роль medic)
    """
    profile = Profile.objects.filter(user=request.user).first()

    # формируем "form" объект (шаблон ждёт .value)
    class _Fld:
        def __init__(self, v): self.value = v if v is not None else ""
    form = SimpleNamespace(
        first_name=_Fld(getattr(profile, "first_name", "") if profile else ""),
        last_name=_Fld(getattr(profile, "last_name", "") if profile else ""),
        middle_name=_Fld(getattr(profile, "middle_name", "") if profile else ""),
        iin=_Fld(getattr(profile, "iin", "") if profile else ""),
        weight=_Fld(getattr(profile, "weight", "") if profile else ""),
        blood_group=_Fld(getattr(profile, "blood_group", "") if profile else ""),
        city=_Fld(getattr(profile, "city", "") if profile else ""),
        address=_Fld(getattr(profile, "address", "") if profile else ""),
        email=_Fld(request.user.email if request.user else ""),
        phone=_Fld(getattr(profile, "phone", "") if profile else ""),
    )

    # получаем employee только если роль медик
    employee = None
    if profile and str(getattr(profile, "role", "")).lower() in ("medic", "медик"):
        # использует метод get_employee() в Profile (если ты добавил ранее)
        try:
            employee = profile.get_employee()
        except Exception:
            employee = None

    context = {
        "mode": "profile",
        "form": form,
        "profile": profile,
        "employee": employee,
        "legacy": None,
    }
    return render(request, "profile.html", context)


def profile_view(request):
    email = (request.user.email or request.user.username).strip()
    
    import os
    from django.template.loader import get_template
    tpl = get_template("profile.html")
    print("=== REAL TEMPLATE PATH ===")
    print(os.path.abspath(tpl.origin.name))
    print("==========================")


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    return Response({"status": "ok"})
