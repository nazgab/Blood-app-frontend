from django.db.models import Q
from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render
from django.db import connection
from django.contrib.auth.decorators import login_required
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
import io
import csv
import os
from django.conf import settings
from django.http import HttpResponse, FileResponse
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

try:
    from core.models import Donation, Center  # поменяйте путь если модели в другом приложении
    ORM_AVAILABLE = True
except Exception:
    Donation = None
    Center = None
    ORM_AVAILABLE = False

# Попытка импортировать legacy user (у вас есть LegacyUser)
try:
    from core.legacy_models import LegacyUser
except Exception:
    try:
        from legacy_models import LegacyUser
    except Exception:
        LegacyUser = None

@login_required
def donations_history(request):
    """
    Показать историю доноров для текущего пользователя.
    Логика получения user_id:
     - сначала пытаемcя найти соответствие в LegacyUser (если есть) по email и брать legacy.user_id,
     - иначе используем request.user.id (обычный Django id).
    Далее получаем список пожертвований (donations) JOIN centers и отдаём в шаблон.
    """
    # определяем какой user_id в таблице donations использовать
    legacy_user_id = None
    if LegacyUser and request.user and request.user.email:
        try:
            lu = LegacyUser.objects.filter(email__iexact=request.user.email).first()
            if lu:
                # в вашей legacy модели поле называется user_id (вы показывали)
                legacy_user_id = getattr(lu, 'user_id', None)
        except Exception:
            legacy_user_id = None

    # если legacy найден — используем его id, иначе используем django user id
    user_id_for_query = legacy_user_id if legacy_user_id is not None else getattr(request.user, 'id', None)

    donations = []

    # 1) Попробуем через ORM, если модель найдена и поле names совпадают
    if ORM_AVAILABLE:
        try:
            # Попробуйте изменить фильтр, если в модели поле называется по-другому (user_id / user)
            qs = Donation.objects.filter(user_id=user_id_for_query).order_by('-donation_date')[:200]
            # если у вас есть ForeignKey к центру: select_related('center')
            try:
                qs = qs.select_related('center')
            except Exception:
                pass

            for d in qs:
                center_name = ''
                # если у модели есть FK center — возьмём его имя
                if hasattr(d, 'center') and d.center:
                    center_name = getattr(d.center, 'center_name', getattr(d.center, 'name', '') )
                else:
                    # возможно center_id поле
                    if hasattr(d, 'center_id'):
                        # попытаемся найти центр через ORM Center, если есть модель
                        try:
                            if Center:
                                c = Center.objects.filter(center_id=d.center_id).first()
                                center_name = getattr(c, 'center_name', '') if c else ''
                        except Exception:
                            center_name = ''
                donations.append({
                    'donation_id': getattr(d, 'donation_id', getattr(d, 'id', None)),
                    'donation_date': getattr(d, 'donation_date', getattr(d, 'date', None)),
                    'volume_ml': getattr(d, 'volume_ml', getattr(d, 'volume', None)),
                    'confirmed': getattr(d, 'confirmed', None),
                    'bonus_points': int(getattr(d, 'bonus_points', 0) or 0),
                    'center_name': center_name,
                })
        except Exception:
            # упал ORM — упадём в raw SQL ниже
            donations = []

    # 2) Если ORM не сработал или не дал данных — делаем raw SQL (надежно)
    if not donations:
        tbl_d = 'donations'
        tbl_c = 'centers'
        sql = f"""
        SELECT d.donation_id, d.user_id, d.center_id, d.donation_date, d.volume_ml, d.confirmed, d.bonus_points,
               c.center_name
        FROM {tbl_d} d
        LEFT JOIN {tbl_c} c ON d.center_id = c.center_id
        WHERE d.user_id = %s
        ORDER BY d.donation_date DESC
        LIMIT 500;
        """
        with connection.cursor() as c:
            c.execute(sql, [user_id_for_query])
            colnames = [col[0] for col in c.description] if c.description else []
            rows = c.fetchall()
            for row in rows:
                # привязываем по именам колонок для устойчивости
                r = dict(zip(colnames, row))
                donations.append({
                    'donation_id': r.get('donation_id'),
                    'donation_date': r.get('donation_date'),
                    'volume_ml': r.get('volume_ml'),
                    'confirmed': r.get('confirmed'),
                    'bonus_points': int(r.get('bonus_points') or 0),
                    'center_name': r.get('center_name') or '',
                })

    # передаём в шаблон
    return render(request, 'history.html', {
        'donations': donations,
    })

try:
    from openpyxl import Workbook
    OPENPYXL_OK = True
except Exception:
    OPENPYXL_OK = False

# для pdf
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

@login_required
def export_history(request):
    """
    Экспорт истории донорства текущего пользователя.
    ?format=xlsx  -> Excel
    ?format=pdf   -> PDF
    ?format=csv   -> CSV (fallback)
    """
    fmt = (request.GET.get('format') or 'xlsx').lower()

    # ---------- определить user_id (как в donations_history) ----------
    legacy_user_id = None
    try:
        from core.legacy_models import LegacyUser
    except Exception:
        try:
            from legacy_models import LegacyUser
        except Exception:
            LegacyUser = None

    if LegacyUser and request.user and request.user.email:
        try:
            lu = LegacyUser.objects.filter(email__iexact=request.user.email).first()
            if lu:
                legacy_user_id = getattr(lu, 'user_id', None)
        except Exception:
            legacy_user_id = None

    user_id_for_query = legacy_user_id if legacy_user_id is not None else getattr(request.user, 'id', None)

    # ---------- собрать donations через raw SQL (надёжно) ----------
    donations = []
    tbl_d = 'donations'
    tbl_c = 'centers'
    sql = f"""
        SELECT d.donation_id, d.user_id, d.center_id, d.donation_date, d.volume_ml, d.confirmed, d.bonus_points,
               c.center_name
        FROM {tbl_d} d
        LEFT JOIN {tbl_c} c ON d.center_id = c.center_id
        WHERE d.user_id = %s
        ORDER BY d.donation_date DESC
        LIMIT 2000;
    """
    from django.db import connection
    with connection.cursor() as c:
        c.execute(sql, [user_id_for_query])
        colnames = [col[0] for col in c.description] if c.description else []
        rows = c.fetchall()
        for row in rows:
            r = dict(zip(colnames, row))
            donations.append({
                'donation_id': r.get('donation_id'),
                'donation_date': r.get('donation_date'),
                'volume_ml': r.get('volume_ml'),
                'confirmed': r.get('confirmed'),
                'bonus_points': r.get('bonus_points') or 0,
                'center_name': r.get('center_name') or '',
            })

    # Преобразуем записи в табличный список (заголовки)
    headers = ['ID', 'Дата', 'Центр', 'Объем (мл)', 'Статус', 'Бонус очки']
    rows_out = []
    for d in donations:
        status = 'Қабылданды' if d['confirmed'] is True else ('Бас тартылды' if d['confirmed'] is False else 'Өңделуде')
        rows_out.append([
            d['donation_id'] or '',
            d['donation_date'].strftime('%Y-%m-%d') if d['donation_date'] else '',
            d['center_name'],
            d['volume_ml'] or '',
            status,
            d['bonus_points'] or 0,
        ])

    # ---------------- XLSX ----------------
    if fmt in ('xlsx', 'excel') and OPENPYXL_OK:
        wb = Workbook()
        ws = wb.active
        ws.title = "Donations"
        ws.append(headers)
        for r in rows_out:
            ws.append(r)
        # auto width (simple)
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        l = len(str(cell.value))
                        if l > max_length: max_length = l
                except Exception:
                    pass
            ws.column_dimensions[col_letter].width = min(50, max(10, max_length + 2))

        bio = io.BytesIO()
        wb.save(bio)
        bio.seek(0)
        resp = HttpResponse(bio.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp['Content-Disposition'] = 'attachment; filename="donations.xlsx"'
        return resp

    # ---------------- PDF ----------------
    if fmt == 'pdf' and REPORTLAB_OK:
        # регистрация шрифта DejaVu (чтобы работала кириллица)
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except Exception as e:
            # fallback: если импорт не прошёл, сообщим
            print("ReportLab font imports failed:", e)
        else:
            # путь к шрифту (BASE_DIR/static/fonts/DejaVuSans.ttf)
            FONT_PATH = os.path.join(getattr(settings, "BASE_DIR", "."), "static", "fonts", "DejaVuSans.ttf")
            if os.path.exists(FONT_PATH):
                try:
                    pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))
                except Exception as e:
                    # зарегистрировать не удалось — выведем в лог (PDF всё равно попытается)
                    print("Failed to register DejaVu font:", e)
            else:
                print("DejaVu font not found at:", FONT_PATH)

        bio = io.BytesIO()
        # альбомная A4
        doc = SimpleDocTemplate(bio, pagesize=landscape(A4), leftMargin=18, rightMargin=18, topMargin=18, bottomMargin=18)

        data = [headers] + rows_out

        # задаём ширины колонок приблизительно (можешь подогнать)
        col_count = len(headers)
        # равномерное распределение, пример:
        table = Table(data, repeatRows=1)  # можно: Table(data, colWidths=[...])

        # стиль: используем DejaVu если зарегистрирован, иначе оставим Helvetica
        font_name = "DejaVu"
        # если шрифт не зарегистрирован — проверка здесь не строгая, но TableStyle просто будет пытаться использовать его
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EAF1FF')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            # используем DejaVu для всей таблицы (включая заголовки)
            ('FONTNAME', (0,0), (-1,0), font_name),
            ('FONTNAME', (0,1), (-1,-1), font_name),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))

        # можно добавить авторазмер колонок — но reportlab требует вычислений; для начала пусть будет так
        doc.build([table])
        bio.seek(0)
        resp = HttpResponse(bio.read(), content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="donations.pdf"'
        return resp


    # ---------------- CSV (fallback) ----------------
    bio = io.StringIO()
    writer = csv.writer(bio)
    writer.writerow(headers)
    for r in rows_out:
        writer.writerow(r)
    resp = HttpResponse(bio.getvalue(), content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="donations.csv"'
    return resp

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    return Response({"status": "ok"})

from django.shortcuts import render
from django.db.models import Q
from core.models import DonationSession

def donate_view(request):
    q = request.GET.get("q", "").strip()

    # язык интерфейса
    lang = request.session.get("lang", "kk")

    sessions = DonationSession.objects.all()

    if q:
        sessions = sessions.filter(
            Q(description__icontains=q)
        )

    context = {
        "sessions": sessions,
        "query": q,
        "lang": lang,
    }
    return render(request, "donate_list.html", context)

