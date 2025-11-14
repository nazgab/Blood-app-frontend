# core/context_processors.py
def site_config(request):
    """
    Возвращает объект SiteConfig в шаблоны (или None, если не найден/ошибка).
    Импорт модели делаем внутри функции, чтобы избежать ошибок импорта при старте.
    """
    try:
        # импорт внутри функции — безопаснее при случайных циклических импортов
        from .models import SiteConfig
        cfg = SiteConfig.objects.first()
    except Exception:
        cfg = None
    return {"site_config": cfg}
