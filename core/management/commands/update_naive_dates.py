from django.core.management.base import BaseCommand
from django.utils import timezone
from core.legacy_models import LegacyUser  # Правильный импорт

class Command(BaseCommand):
    help = 'Преобразует наивные даты в aware даты'

    def handle(self, *args, **kwargs):
        users = LegacyUser.objects.filter(created_at__isnull=False)
        count = 0

        for user in users:
            if timezone.is_naive(user.created_at):  # Проверяем, наивная ли дата
                user.created_at = timezone.make_aware(user.created_at, timezone.get_current_timezone())
                user.save()
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Обновлено {count} записей'))
