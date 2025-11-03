from django.contrib import admin
from django.contrib.admin import AdminSite
from . import models
from .models import AboutSection
from .legacy_models import LegacyUser
import csv
from django.http import HttpResponse
from django.http import HttpResponseForbidden
import logging
from import_export import resources
from import_export.admin import ExportMixin
from import_export.formats.base_formats import XLSX
from django.utils import timezone
from django.db.models import F, Value
from django.db.models.functions import Concat, Coalesce, Lower
from django.db.models.expressions import Func
from django.db import DatabaseError
from django.db import models as dj_models

# Попытка импортировать Collate (Django 3.2+)
try:
    from django.db.models.functions import Collate

    HAS_COLLATE = True
except ImportError:
    HAS_COLLATE = False


@admin.register(models.SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at")
    fields = ("logo", "footer_text_kk", "footer_text_ru", "footer_text_en")


@admin.register(models.MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("key", "title_ru", "order", "visible")
    list_editable = ("order", "visible")
    fields = ("key", "title_kk", "title_ru", "title_en", "href", "order", "visible")


@admin.register(models.HeroBlock)
class HeroBlockAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "updated_at")
    fields = (
        "title_kk",
        "title_ru",
        "title_en",
        "subtitle_kk",
        "subtitle_ru",
        "subtitle_en",
        "cta_text_kk",
        "cta_text_ru",
        "cta_text_en",
        "cta_url",
    )


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title_ru", "category", "is_published", "published_at")
    prepopulated_fields = {"slug": ("title_ru",)}
    list_filter = ("category", "is_published")
    search_fields = ("title_ru", "title_kk")


@admin.register(models.BloodCenter)
class BloodCenterAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "city", "is_active")
    list_filter = ("city", "is_active")
    search_fields = ("name_ru", "name_kk", "city")


@admin.register(models.ContactChannel)
class ContactChannelAdmin(admin.ModelAdmin):
    list_display = ("kind", "value", "order")
    list_editable = ("order",)


@admin.register(models.BonusAccount)
class BonusAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "level", "updated_at")
    search_fields = ("user__email",)


@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ["updated_at"]


# Настроим логгер
logger = logging.getLogger(__name__)


# Функция для логирования изменений
def log_change(request, action, donor):
    logger.info(
        f"Пользователь {request.user.username} {action} донор: {donor.id} - {donor.name}"
    )


# Ресурс для экспорта в Excel
class LegacyUserResource(resources.ModelResource):
    class Meta:
        model = LegacyUser
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "blood_group",
            "iin",
            "rh_factor",
            "city",
            "address",
            "phone",
            "email",
            "created_at",
        )
        export_order = (
            "user_id",
            "first_name",
            "last_name",
            "blood_group",
            "iin",
            "rh_factor",
            "city",
            "address",
            "phone",
            "email",
            "created_at",
        )


COLLATION_NAME = "kk_KZ.utf8"


class TextConcat(Func):
    """
    Рендерит IMMUTABLE-эквивалент CONCAT:
    (COALESCE(expr1,'') || ' ' || COALESCE(expr2,''))
    """

    arity = 2
    output_field = dj_models.CharField()
    template = (
        "(COALESCE(%(expressions)s, '') || ' ' || COALESCE(%(expressions)s_1, ''))"
    )


class RawCollate(Func):
    """
    Обходит строгую валидацию Django Collate:
    (<expr>) COLLATE "kk_KZ.utf8"
    """

    arity = 1
    template = f'(%(expressions)s) COLLATE "{COLLATION_NAME}"'
    output_field = dj_models.CharField()


# Функция для обработки изменений данных в админке
@admin.register(LegacyUser)
class LegacyUserAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        "user_id",
        "full_name_display",  # <- показываем ФИО из метода ниже
        "blood_group",
        "iin",
        "rh_factor_display",
        "city",
        "address",
        "phone",
        "email",
        "created_at_display",
    )

    # чтобы применялся order_by из get_queryset
    ordering = ()

    # ---------- отображение колонок ----------
    def full_name_display(self, obj):
        ln = (obj.last_name or "").strip()
        fn = (obj.first_name or "").strip()
        return f"{ln} {fn}".strip()

    full_name_display.short_description = "Аты-жөні"
    full_name_display.admin_order_field = "full_name_order"  # сортируем по аннотации

    def rh_factor_display(self, obj):
        return getattr(obj, "rh_factor", "-")

    rh_factor_display.short_description = "Резус-фактор"

    def created_at_display(self, obj):
        return timezone.localtime(obj.created_at) if obj.created_at else "-"

    created_at_display.short_description = "Тіркелу күні"

    # ---------- правильная сортировка ----------
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Собираем "Фамилия Имя" безопасно через ORM
        full_expr = Concat(
            Coalesce(F("last_name"), Value("")),
            Value(" "),
            Coalesce(F("first_name"), Value("")),
        )

        # Пытаемся применить казахскую/русскую коллацию к ЦЕЛОМУ выражению
        if HAS_COLLATE:
            for col in ("kk_KZ.utf8", "ru_RU.utf8"):
                try:
                    qs2 = qs.annotate(full_name_order=Collate(full_expr, col))
                    # Одно обращение к БД, чтобы отловить проблемы сразу
                    list(qs2.values_list("full_name_order")[:1])
                    return qs2.order_by("full_name_order")
                except Exception:
                    continue

        # Фоллбек: стабильная сортировка по lower()
        return qs.annotate(full_name_order=Lower(full_expr)).order_by("full_name_order")

    # ---------- остальное ----------
    search_fields = (
        "first_name",
        "last_name",
        "city",
        "iin",
        "email",
        "phone",
        "blood_group",
    )
    list_filter = ("blood_group", "city")
    date_hierarchy = "created_at"
    list_per_page = 25
    actions = ["make_admin", "export_legacy_users_csv", "export_legacy_users_excel"]

    def make_admin(self, request, queryset):
        queryset.update(role="admin")

    make_admin.short_description = "Назначить роль 'admin' для выбранных доноров"

    # --- экспорт CSV ---
    def export_legacy_users_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="donors_legacy.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "ID",
                "Аты-жөні",
                "Қан тобы",
                "ИИН",
                "Резус",
                "Қала",
                "Адрес",
                "Телефон",
                "Email",
                "Тіркелу күні",
            ]
        )
        for u in queryset:
            full_name = (
                f"{(u.last_name or '').strip()} {(u.first_name or '').strip()}".strip()
            )
            rh = getattr(u, "rh_factor", "-")
            writer.writerow(
                [
                    u.user_id,
                    full_name,
                    u.blood_group,
                    u.iin,
                    rh,
                    u.city,
                    u.address or "",
                    u.phone or "",
                    u.email,
                    u.created_at,
                ]
            )
        return response

    export_legacy_users_csv.short_description = "Экспорт (CSV)"

    # --- экспорт Excel ---
    # --- экспорт Excel ---
    def export_legacy_users_excel(self, request, queryset):
        dataset = LegacyUserResource().export(queryset)
        # БЫЛО: dataset.xlsx  -> AttributeError
        data = dataset.export('xlsx')  # bytes

        return HttpResponse(
            data,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="donors_legacy.xlsx"'},
        )

    export_legacy_users_excel.short_description = "Экспорт (Excel)"

