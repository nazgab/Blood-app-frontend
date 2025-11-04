from django.db import models
from django.utils import timezone


class LegacyUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=5)
    iin = models.CharField(max_length=12, unique=True)
    age = models.IntegerField()
    weight = models.IntegerField()
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)  
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.email})"

    # Переводим дату в aware datetime (с временной зоной)
    def save(self, *args, **kwargs):
        if self.created_at and timezone.is_naive(self.created_at):
            self.created_at = timezone.make_aware(
                self.created_at, timezone.get_current_timezone()
            )
        super().save(*args, **kwargs)


class Center(models.Model):
    center_id = models.AutoField(primary_key=True)
    center_name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=6, blank=True, null=True
    )
    contact = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "centers"

    def __str__(self):
        return self.center_name


class Donation(models.Model):
    donation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        LegacyUser,
        on_delete=models.DO_NOTHING,
        db_column="user_id",
        related_name="donations",
    )
    center = models.ForeignKey(
        Center,
        on_delete=models.DO_NOTHING,
        db_column="center_id",
        related_name="donations",
    )
    donation_date = models.DateField()
    volume_ml = models.IntegerField(default=450)
    confirmed = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "donations"


class Bonus(models.Model):
    bonus_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        LegacyUser,
        on_delete=models.DO_NOTHING,
        db_column="user_id",
        related_name="bonuses",
    )
    points = models.IntegerField(default=0)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "bonuses"
