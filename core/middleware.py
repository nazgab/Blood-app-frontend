# core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden

MEDIC_PATH_PREFIX = '/medic/'

class RequireMedicRoleMiddleware:
    """
    Если путь начинается с /medic/ — требует аутентификацию и роль medic или is_staff.
    - если не аутентифицирован — редиректит на логин с ?next=
    - если аутентифицирован, но не medic/is_staff — возвращает 403 Forbidden
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or ''
        # проверяем только страницы/эндпоинты начинающиеся на /medic/
        if path.startswith(MEDIC_PATH_PREFIX):
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                login_url = reverse('login')
                return redirect(f"{login_url}?next={request.path}")
            profile = getattr(user, 'profile', None)
            if not (getattr(user, 'is_staff', False) or getattr(profile, 'role', '') == 'medic'):
                return HttpResponseForbidden("Доступ запрещён: требуется роль medic.")
        return self.get_response(request)
