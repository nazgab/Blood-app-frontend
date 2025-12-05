from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

LANG_CHOICES = (("kk", "Kazakh"), ("ru", "Russian"))


class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteConfig(Timestamped):
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    app_link_android = models.URLField(blank=True)
    app_link_ios = models.URLField(blank=True)
    footer_text_kk = models.TextField(blank=True, default="")
    footer_text_ru = models.TextField(blank=True, default="")
    footer_text_en = models.TextField(blank=True, default="")

    def __str__(self):
        return f"SiteConfig #{self.id}"


class MenuItem(models.Model):
    key = models.SlugField(unique=True)
    title_kk = models.CharField(max_length=100)
    title_ru = models.CharField(max_length=100)
    # 🔽 новое поле
    title_en = models.CharField(max_length=100, blank=True, default="")

    href = models.CharField(max_length=200, help_text="Path or URL")
    order = models.PositiveIntegerField(default=0)
    visible = models.BooleanField(default=True)

    def __str__(self):
        # покажем что-то осмысленное
        return self.title_ru or self.title_kk or self.title_en

    class Meta:
        ordering = ["order", "id"]


class HeroBlock(models.Model):
    # ...
    title_kk = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200, blank=True, default="")  # 🔽

    subtitle_kk = models.CharField(max_length=300, blank=True, default="")
    subtitle_ru = models.CharField(max_length=300, blank=True, default="")
    subtitle_en = models.CharField(max_length=300, blank=True, default="")  # 🔽

    cta_text_kk = models.CharField(max_length=100, blank=True, default="")
    cta_text_ru = models.CharField(max_length=100, blank=True, default="")
    cta_text_en = models.CharField(max_length=100, blank=True, default="")  # 🔽

    cta_url = models.CharField(max_length=200, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)


class Article(Timestamped):
    CATEGORY_CHOICES = (
        ("advice", "Медициналық кеңестер / Медицинские советы"),
        ("event", "Акциялар / Акции"),
        ("news", "Жаңалықтар / Новости"),
    )
    title_kk = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt_kk = models.CharField(max_length=300, blank=True, default="")
    excerpt_ru = models.CharField(max_length=300, blank=True, default="")
    body_kk = models.TextField()
    body_ru = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="news")
    cover = models.ImageField(upload_to="articles/", blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title_ru or self.title_kk

    class Meta:
        ordering = ["-published_at", "-id"]


class BloodCenter(Timestamped):
    name_kk = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=50, blank=True, default="")
    hours_kk = models.CharField(max_length=120, blank=True, default="")
    hours_ru = models.CharField(max_length=120, blank=True, default="")
    geo_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geo_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name_ru or self.name_kk


class ContactChannel(models.Model):
    kind = models.CharField(
        max_length=30, help_text="phone, email, whatsapp, telegram..."
    )
    value = models.CharField(max_length=120)
    label_kk = models.CharField(max_length=120, blank=True, default="")
    label_ru = models.CharField(max_length=120, blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.kind}: {self.value}"


User = get_user_model()


class BonusAccount(Timestamped):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="bonus_account"
    )
    balance = models.IntegerField(default=0)
    level = models.CharField(max_length=30, default="Basic")

    def __str__(self):
        return f"{self.user_id} -> {self.balance}"

class AboutSection(models.Model):
    text_kk = models.TextField(verbose_name="О нас (Казахский)")
    text_ru = models.TextField(verbose_name="О нас (Русский)")
    text_en = models.TextField(verbose_name="О нас (Английский)")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"О нас (обновлено {self.updated_at:%Y-%m-%d})"
    
class Profile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name  = models.CharField(max_length=50, blank=True)
    last_name   = models.CharField(max_length=50, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    iin         = models.CharField(max_length=12, blank=True)
    age         = models.IntegerField(blank=True, null=True)
    weight      = models.IntegerField(blank=True, null=True)
    city        = models.CharField(max_length=100, blank=True)
    address     = models.CharField(max_length=255, blank=True)
    phone       = models.CharField(max_length=20, blank=True)

    # опционально — связь с legacy пользователем по id (чтобы знать источник)
    legacy_user_id = models.IntegerField(blank=True, null=True, db_index=True)

    # ===== добавляем роль =====
    ROLE_CHOICES = (
        ("user", "Обычный пользователь"),
        ("medic", "Медик"),
        ("admin", "Админ"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    # ===== поле для привязки к employees =====
    # будем хранить employee.employee_id сюда (опционально, null)
    employee_id = models.IntegerField(blank=True, null=True, db_index=True)

    def is_medic(self):
        return self.role == "medic"

    def get_employee(self):
        """
        Возвращает объект Employee, если он существует:
         - сначала пытаемся по employee_id (если заполнено),
         - затем по совпадению имени+фамилии (fallback).
        """
        from .models import Employee  # локальный импорт чтобы не было циклов

        if self.employee_id:
            emp = Employee.objects.filter(employee_id=self.employee_id).first()
            if emp:
                return emp

        # fallback: поиск по имени/фамилии (чувствителен к совпадению)
        if self.first_name and self.last_name:
            return Employee.objects.filter(
                first_name=self.first_name,
                last_name=self.last_name
            ).first()

        return None

    def __str__(self):
        return f"Profile({self.user.username})"

  
class AdminDonation(models.Model):
    admin_donation_id = models.AutoField(primary_key=True, db_column='admin_donation_id')
    user_id = models.IntegerField(db_column='user_id', db_index=True)
    iin = models.CharField(max_length=20, blank=True, null=True, db_column='iin')
    blood_group = models.CharField(max_length=10, blank=True, null=True, db_column='blood_group')
    center_id = models.IntegerField(blank=True, null=True, db_column='center_id')
    employee_id = models.IntegerField(blank=True, null=True, db_column='employee_id')

    class Meta:
        db_table = "admin_donations"
        managed = False  # таблица уже есть в базе  

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    position = models.CharField(max_length=100)
    center_id = models.IntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'employees'
        managed = False

    def __str__(self):
        return f"Employee({self.employee_id}) {self.first_name} {self.last_name}"

class DonationSession(models.Model):
    session_id = models.AutoField(primary_key=True)

    center = models.ForeignKey(
        'core.BloodCenter',
        on_delete=models.CASCADE,
        db_column='center_id'
    )

    date = models.DateField()
    time_from = models.TimeField(db_column='time_from')
    time_to = models.TimeField(db_column='time_to')
    room = models.CharField(max_length=50)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'donation_sessions'
