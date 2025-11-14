# core/auth_backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.db import transaction
from .legacy_models import LegacyUser
import logging

logger = logging.getLogger(__name__)


class LegacyUserBackend(BaseBackend):
    """
    Backend который:
    - ищет пользователя в legacy-таблице по email (без учёта регистра);
    - проверяет пароль через django.contrib.auth.hashers.check_password
      (поддерживает pbkdf2_sha256 и другие стандартные форматы);
    - при успешной проверке создаёт/получает django.User и копирует
      legacy password hash в user.password (чтобы дальнейшая аутентификация
      шла уже по стандартной таблице).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # логиним по email без учёта регистра и лишних пробелов
        email = (username or kwargs.get("email") or "").strip().lower()
        if not email or not password:
            return None

        try:
            # если legacy в другой БД, можно использовать .using("legacy")
            legacy = LegacyUser.objects.get(email__iexact=email)
        except LegacyUser.DoesNotExist:
            return None

        # legacy.password_hash должен быть в формате Django (например pbkdf2_sha256$...)
        if not check_password(password, legacy.password_hash):
            return None

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    "email": email,
                    "first_name": legacy.first_name or "",
                    "last_name": legacy.last_name or "",
                    "is_active": True,
                },
            )

            # Если пользователь только что создан — безопасно скопировать legacy-хеш
            # Также копируем, если user не имеет usable password или хеш отличается
            try:
                need_save = False
                if created:
                    user.password = legacy.password_hash
                    need_save = True
                else:
                    # не перезаписываем чужой пароль, если он уже установлен и совпадает
                    if (not user.has_usable_password()) or (user.password != legacy.password_hash):
                        user.password = legacy.password_hash
                        need_save = True

                # Если first_name/last_name пусты, попытаться заполнить
                if not user.first_name and legacy.first_name:
                    user.first_name = legacy.first_name
                    need_save = True
                if not user.last_name and legacy.last_name:
                    user.last_name = legacy.last_name
                    need_save = True

                if need_save:
                    # сохраняем только изменённые поля
                    user.save(update_fields=["password", "first_name", "last_name"])
            except Exception as ex:
                # не ломаем логин из-за проблем с обновлением user-поля
                logger.exception("Ошибка при обновлении django.User после legacy-login: %s", ex)

            # --- автосоздание/заполнение Profile из legacy ---
            # импорт внутри блока чтобы не падать, если модели нет
            try:
                from .models import Profile

                profile, _ = Profile.objects.get_or_create(user=user)

                # если профиль ещё не линкуется с legacy — подтянем данные один раз
                if getattr(profile, "legacy_user_id", None) is None:
                    profile.legacy_user_id = legacy.user_id
                    profile.first_name = legacy.first_name or ""
                    profile.last_name = legacy.last_name or ""
                    profile.blood_group = legacy.blood_group or ""
                    profile.iin = legacy.iin or ""
                    profile.age = legacy.age
                    profile.weight = legacy.weight
                    profile.city = legacy.city or ""
                    profile.address = legacy.address or ""
                    profile.phone = legacy.phone or ""
                    profile.save()
            except Exception:
                # не роняем логин, если профиля ещё нет или что-то не так
                pass
            # --- конец автосоздания профиля ---

        logger.debug("Legacy login success for %s (legacy id=%s, created=%s)", email, getattr(legacy, "user_id", None), created)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
