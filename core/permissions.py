# core/permissions.py
from rest_framework import permissions

class IsMedicOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ только staff (is_staff) или пользователям с profile.role == 'medic'.
    Требует аутентификацию.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        profile = getattr(user, "profile", None)
        return getattr(profile, "role", "") == "medic"
