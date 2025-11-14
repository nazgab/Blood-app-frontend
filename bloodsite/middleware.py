# bloodsite/middleware.py
class NoCacheForAuthenticatedMiddleware:
    """
    Для всех ответов, где пользователь аутентифицирован,
    добавляем заголовки чтобы браузер/прокси не кэшировали страницу.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if request.user.is_authenticated:
                response.setdefault("Cache-Control", "no-cache, no-store, must-revalidate")
                response.setdefault("Pragma", "no-cache")
                response.setdefault("Expires", "0")
        except Exception:
            # безопасно — не ломаем обработку запроса
            pass
        return response
