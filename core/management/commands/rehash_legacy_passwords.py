from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.contrib.auth.hashers import make_password
import csv
import secrets
import string

ALPH = string.ascii_letters + string.digits

def gen_password(n=12):
    # Безопасный случайный пароль
    return ''.join(secrets.choice(ALPH) for _ in range(n))

class Command(BaseCommand):
    help = (
        "Перехэшировать пароли в таблице public.users -> password_hash "
        "в формат Django (pbkdf2_sha256). Можно задать один общий пароль "
        "или сгенерировать случайные и выгрузить их в CSV."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--static", dest="static_password", required=True,
            help="One password for ALL users (hash is computed ONCE, then single UPDATE)."
        )

    def handle(self, *args, **opts):
        plain = opts["static_password"]
        self.stdout.write("Генерирую хэш один раз…")
        hashed = make_password(plain)

        self.stdout.write("Обновляю таблицу public.users одним запросом…")
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute("UPDATE public.users SET password_hash=%s", [hashed])

        self.stdout.write(self.style.SUCCESS("Готово: всем пользователям установлен новый Django-хэш."))
