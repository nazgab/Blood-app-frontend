from django.contrib import admin
from . import models
from .models import AboutSection

@admin.register(models.SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("id","updated_at")
    fields = ("logo", "footer_text_kk", "footer_text_ru", "footer_text_en")

@admin.register(models.MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("key","title_ru","order","visible")
    list_editable = ("order","visible")
    fields = ("key", "title_kk", "title_ru", "title_en", "href", "order", "visible")

@admin.register(models.HeroBlock)
class HeroBlockAdmin(admin.ModelAdmin):
    list_display = ("id","title_ru","updated_at")
    fields = (
        "title_kk", "title_ru", "title_en",
        "subtitle_kk", "subtitle_ru", "subtitle_en",
        "cta_text_kk", "cta_text_ru", "cta_text_en",
        "cta_url",
    )

@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title_ru","category","is_published","published_at")
    prepopulated_fields = {"slug": ("title_ru",)}
    list_filter = ("category","is_published")
    search_fields = ("title_ru","title_kk")

@admin.register(models.BloodCenter)
class BloodCenterAdmin(admin.ModelAdmin):
    list_display = ("name_ru","city","is_active")
    list_filter = ("city","is_active")
    search_fields = ("name_ru","name_kk","city")

@admin.register(models.ContactChannel)
class ContactChannelAdmin(admin.ModelAdmin):
    list_display = ("kind","value","order")
    list_editable = ("order",)

@admin.register(models.BonusAccount)
class BonusAccountAdmin(admin.ModelAdmin):
    list_display = ("user","balance","level","updated_at")
    search_fields = ("user__email",)

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['updated_at']