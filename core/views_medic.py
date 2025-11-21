# core/views_medic.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

# предполагается, что LegacyUser модель и сериализатор лежат в core. 
# Если у вас другие пути — поправьте импорты:
from .legacy_models import LegacyUser
# если есть сериализатор:
try:
    from .legacy_serializers import LegacyUserSerializer
except Exception:
    LegacyUserSerializer = None

@login_required
def medic_home(request):
    # is_medic true если профиль отмечен как medic
    is_medic = getattr(getattr(request.user, "profile", None), "role", "") == "medic"
    return render(request, "home.html", {"is_medic": is_medic})

@login_required
def medic_users(request):
    is_medic = getattr(getattr(request.user, "profile", None), "role", "") == "medic"
    return render(request, "medic_users.html", {"is_medic": is_medic})


@login_required
def medic_donations(request):
    # можно дополнительно проверять user.profile.role == 'medic'
    is_medic = getattr(getattr(request.user, 'profile', None), 'role', '') == 'medic'
    return render(request, 'medic_donations.html', {'is_medic': is_medic})

class MedicLegacyUserListView(generics.ListAPIView):
    """
    API для /api/v1/medic/legacy-users/ — возвращает legacy users только для медиков (или staff).
    Поддерживает простые query params:
      - q  (по имени / iin / email)
      - city
      - blood_group
    """
    serializer_class = LegacyUserSerializer if LegacyUserSerializer is not None else None
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        is_medic = getattr(getattr(user, "profile", None), "role", "") == "medic"
        if not (is_medic or user.is_staff):
            return LegacyUser.objects.none()

        qs = LegacyUser.objects.all().order_by("-user_id")  # или .order_by('-id') — как вам удобнее

        q = self.request.query_params.get("q")
        city = self.request.query_params.get("city")
        bg = self.request.query_params.get("blood_group")
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(iin__icontains=q) |
                Q(email__icontains=q)
            )
        if city:
            qs = qs.filter(city__iexact=city)
        if bg:
            qs = qs.filter(blood_group__iexact=bg)
        return qs

    # если сериализатора нет (редко), fallback — вернуть пустой queryset handled above


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def medic_export_users_csv(request):
    """
    Экспорт CSV для медиков. URL: /api/v1/medic/legacy-users/export/csv/
    """
    user = request.user
    is_medic = getattr(getattr(user, "profile", None), "role", "") == "medic"
    if not (is_medic or user.is_staff):
        return Response(status=403)

    qs = LegacyUser.objects.all().order_by("user_id")

    # можно применить фильтры так же как в списке (по q/city/blood_group)
    q = request.query_params.get("q")
    city = request.query_params.get("city")
    bg = request.query_params.get("blood_group")
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(iin__icontains=q) |
            Q(email__icontains=q)
        )
    if city:
        qs = qs.filter(city__iexact=city)
    if bg:
        qs = qs.filter(blood_group__iexact=bg)

    # response CSV
    import csv
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="legacy_users.csv"'

    writer = csv.writer(response)
    # заголовок — подставьте поля вашей модели
    writer.writerow(["user_id", "first_name", "last_name", "blood_group", "iin", "city", "phone", "email"])

    for u in qs:
        # замените атрибуты на реальные поля вашей модели LegacyUser
        writer.writerow([
            getattr(u, "user_id", getattr(u, "id", "")),
            getattr(u, "first_name", ""),
            getattr(u, "last_name", ""),
            getattr(u, "blood_group", ""),
            getattr(u, "iin", ""),
            getattr(u, "city", ""),
            getattr(u, "phone", ""),
            getattr(u, "email", "")
        ])
    return response

