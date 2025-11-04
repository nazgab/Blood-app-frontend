# core/auth_backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.db import transaction
from .legacy_models import LegacyUser

class LegacyUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # логиним по email без учёта регистра и лишних пробелов
        email = (username or kwargs.get("email") or "").strip().lower()
        if not email or not password:
            return None

        try:
            # если нужно без регистра:
            legacy = LegacyUser.objects.get(email__iexact=email)
            # если legacy в другой БД, используй:
            # legacy = LegacyUser.objects.using("legacy").get(email__iexact=email)
        except LegacyUser.DoesNotExist:
            return None

        if not check_password(password, legacy.password_hash):
            return None

        with transaction.atomic():
            user, _ = User.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "first_name": legacy.first_name or "",
                    "last_name":  legacy.last_name  or "",
                    "is_active":  True,
                },
            )

            # --- ВСТАВКА: автосоздание/заполнение Profile из legacy ---
            # импорт внутри try, чтобы не падать, если Profile ещё не создан
            try:
                from .models import Profile
                profile, _ = Profile.objects.get_or_create(user=user)

                # если профиль ещё не линкуется с legacy — подтянем данные один раз
                if getattr(profile, "legacy_user_id", None) is None:
                    profile.legacy_user_id = legacy.user_id
                    profile.first_name     = legacy.first_name or ""
                    profile.last_name      = legacy.last_name  or ""
                    profile.blood_group    = legacy.blood_group or ""
                    profile.iin            = legacy.iin or ""
                    profile.age            = legacy.age
                    profile.weight         = legacy.weight
                    profile.city           = legacy.city or ""
                    profile.address        = legacy.address or ""
                    profile.phone          = legacy.phone or ""
                    profile.save()
            except Exception:
                # не роняем логин, если профиля ещё нет или что-то не так
                pass
            # --- КОНЕЦ ВСТАВКИ ---

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
