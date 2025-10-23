from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core Content"

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_save
        from .models import BonusAccount

        User = get_user_model()

        def create_bonus(sender, instance, created, **kwargs):
            if created:
                BonusAccount.objects.get_or_create(user=instance)

        post_save.connect(create_bonus, sender=User, weak=False)
