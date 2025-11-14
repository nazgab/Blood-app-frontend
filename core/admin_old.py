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


# Функция для обработки изменений данных в админке
@admin.register(LegacyUser)
class LegacyUserAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        "user_id",
        "full_name",
        "blood_group",
        "iin",
        "rh_factor",
        "city",
        "address",
        "phone",
        "email",
        "created_at",
    )

    # Метод для отображения полного имени
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    full_name.short_description = "Аты-жөні"  # Переименовываем для админки
    full_name.admin_order_field = "last_name"  # Сортировка по фамилии

    # Метод для отображения резус-фактора, если его нет, показываем "-"
    def rh_factor(self, obj):
        return getattr(obj, "rh_factor", "-")  # Если поля нет, возвращаем "-"

    rh_factor.short_description = "Резус-фактор"

    # Метод для отображения времени с учётом временной зоны
    def created_at(self, obj):
        if obj.created_at:
            return timezone.localtime(obj.created_at)  # Преобразуем в локальное время
        return "-"

    created_at.short_description = "Тіркелу күні"

    # Поиск и фильтры
    search_fields = (
        "first_name",
        "last_name",
        "city",
        "iin",
        "email",
        "phone",
        "blood_group",
    )
    list_filter = ("blood_group", "city")  # Фильтрация по группе крови и городу
    date_hierarchy = "created_at"  # Иерархия по дате регистрации
    list_per_page = 25  # Пагинация по 25 записей на странице
    ordering = ("-created_at",)  # Сортировка по дате регистрации

    actions = ["make_admin", "export_legacy_users_csv", "export_legacy_users_excel"]

    def make_admin(self, request, queryset):
        queryset.update(role="admin")  # Изменяем роль на 'admin' для выбранных записей

    make_admin.short_description = "Назначить роль 'admin' для выбранных доноров"

    # Функция для экспорта выбранных данных в CSV
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
            full_name = f"{u.last_name} {u.first_name}".strip()  # Получаем полное имя
            rh = getattr(u, "rh_factor", "-")  # Если резус-фактор есть, используем его
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

    # Функция для экспорта в Excel
    def export_legacy_users_excel(self, request, queryset):
        dataset = LegacyUserResource().export(
            queryset
        )  # Экспортируем данные с помощью нашего ресурса
        response = HttpResponse(
            dataset.xlsx,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="donors_legacy.xlsx"'
        return response

    export_legacy_users_excel.short_description = "Экспорт (Excel)"
