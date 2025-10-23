# core/auth_backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from .legacy_models import LegacyUser

User = get_user_model()

class LegacyUserBackend(ModelBackend):
    """
    Аутентифицируемся по public.users:
    - ищем пользователя по email (или username = email)
    - проверяем пароль check_password против password_hash из таблицы users
    - при первом входе создаём/находим Django User с таким же email
    """
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        login = (email or username or "").strip().lower()
        if not login or not password:
            return None

        try:
            lu = LegacyUser.objects.get(email__iexact=login)
        except LegacyUser.DoesNotExist:
            return None

        # password_hash уже в формате Django (pbkdf2_sha256...), т.к. ты его перехэшировал
        if not check_password(password, lu.password_hash):
            return None

        # создаём/находим «тень» в auth_user (для JWT и прав)
        user, _created = User.objects.get_or_create(
            username=login,
            defaults={
                "email": login,
                "first_name": lu.first_name,
                "last_name":  lu.last_name,
                "is_active": True,
            },
        )
        return user
