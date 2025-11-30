from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from .legacy_models import Center
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import AdminDonation
from .serializers import DonationSerializer
from .permissions import IsMedicOrAdmin
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

# legacy imports (optional)
from .legacy_models import LegacyUser
try:
    from .legacy_serializers import LegacyUserSerializer
except Exception:
    LegacyUserSerializer = None

class MedicLegacyPagination(PageNumberPagination):
    # по умолчанию пусть сервер возвращает крупные блоки, чтобы фронт мог брать больше сразу
    page_size = 1000                 # значение по умолчанию при отсутствии ?page_size=
    page_size_query_param = 'page_size'  # позволяет клиенту указывать ?page_size=...
    max_page_size = 10000            # максимум, который клиент может запросить

@login_required
def medic_home(request):
    is_medic = getattr(getattr(request.user, "profile", None), "role", "") == "medic"
    return render(request, "home.html", {"is_medic": is_medic})


@login_required
def medic_users(request):
    is_medic = getattr(getattr(request.user, "profile", None), "role", "") == "medic"
    return render(request, "medic_users.html", {"is_medic": is_medic})


@login_required
def medic_donations(request):
    is_medic = getattr(getattr(request.user, 'profile', None), 'role', '') == 'medic'
    return render(request, 'medic_donations.html', {'is_medic': is_medic})


class MedicLegacyUserListView(generics.ListAPIView):
    serializer_class = LegacyUserSerializer if LegacyUserSerializer is not None else None
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MedicLegacyPagination

    def get_queryset(self):
        user = self.request.user
        is_medic = getattr(getattr(user, "profile", None), "role", "") == "medic"
        if not (is_medic or user.is_staff):
            return LegacyUser.objects.none()

        qs = LegacyUser.objects.all().order_by("-user_id")

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


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def medic_export_users_csv(request):
    user = request.user
    is_medic = getattr(getattr(user, "profile", None), "role", "") == "medic"
    if not (is_medic or user.is_staff):
        return Response(status=403)

    qs = LegacyUser.objects.all().order_by("user_id")

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

    import csv
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="legacy_users.csv"'

    writer = csv.writer(response)
    writer.writerow(["user_id", "first_name", "last_name", "blood_group", "iin", "city", "phone", "email"])

    for u in qs:
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


class MedicDonationsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.GET.get('q', '').strip()
        center = request.GET.get('center', '').strip()

        qs = AdminDonation.objects.all().order_by('-admin_donation_id')
        if center:
            qs = qs.filter(center_id=center)
        if q:
            qs = qs.filter(iin__icontains=q)

        user_ids = list({d.user_id for d in qs if d.user_id})
        users = User.objects.filter(id__in=user_ids).in_bulk()

        result = []
        for d in qs[:500]:
            u = users.get(d.user_id)
            obj = {
                "admin_donation_id": d.admin_donation_id,
                "user_id": d.user_id,
                "iin": d.iin,
                "blood_group": d.blood_group,
                "center_id": d.center_id,
                "employee_id": d.employee_id,
                # если хотите — можно подставлять имя из legacy или из связанной таблицы:
                "first_name": u.first_name if u else None,
                "last_name": u.last_name if u else None,
            }
            result.append(obj)

        return Response(result)

        

@api_view(['GET'])
@permission_classes([IsMedicOrAdmin])
def medic_used_centers(request):
    """
    Возвращает список центров, которые действительно используются в admin_donations.
    Формат: [{ "center_id": 1, "center_name": "...", "contact": "..." }, ...]
    Работает даже если legacy Center модель хранит поля по-разному (id/name/center_id).
    """
    center_ids_qs = AdminDonation.objects.values_list('center_id', flat=True).distinct()
    # фильтруем None и приводим к int, если возможно
    center_ids = []
    for v in center_ids_qs:
        if v is None:
            continue
        try:
            center_ids.append(int(v))
        except Exception:
            # если уже int или не приводится — сохраняем как есть
            center_ids.append(v)

    # Попробуем получить реальные записи из модели Center (если модель есть)
    centers_out = []
    try:
        if Center is not None:
            # сначала подберём возможные поля для фильтра
            # если в модели есть center_id поле — используем его, иначе id
            if hasattr(Center, 'center_id'):
                qs = Center.objects.filter(center_id__in=center_ids)
            else:
                qs = Center.objects.filter(pk__in=center_ids)

            # выбираем многие поля — но потом нормализуем
            for c in qs:
                # попытка получить удобное имя
                name = getattr(c, 'center_name', None) or getattr(c, 'name_ru', None) or getattr(c, 'name', None) or getattr(c, 'centerName', None)
                contact = getattr(c, 'contact', None) or getattr(c, 'address', None) or ""
                cid = getattr(c, 'center_id', None) or getattr(c, 'pk', None) or getattr(c, 'id', None)
                try:
                    cid = int(cid)
                except Exception:
                    pass
                centers_out.append({
                    "center_id": cid,
                    "center_name": name or f"Центр {cid}",
                    "contact": contact or ""
                })
    except Exception:
        # если что-то упало при попытке достать Center — просто вернём id'шники
        pass

    # fallback: если не нашли ни одной записи — вернуть просто уникальные id из admin_donations
    if not centers_out:
        centers_out = [{"center_id": int(cid) if isinstance(cid, (str, int)) and str(cid).isdigit() else cid,
                        "center_name": f"Центр {cid}",
                        "contact": ""} for cid in sorted(set(center_ids)) if cid is not None]

    return Response(centers_out)


@api_view(['GET'])
@permission_classes([IsMedicOrAdmin])
def medic_donation_donors(request):
    """
    Возвращает список уникальных доноров (user_id + iin + опционально имя) из admin_donations.
    Формат: [{ "user_id": 123, "iin": "123...", "first_name": "...", "last_name": "..." }, ...]
    """
    # берём последние записи и получаем user_id + iin
    qs = AdminDonation.objects.order_by('-admin_donation_id').values('user_id', 'iin')

    out = []
    seen = set()
    user_ids = []
    for item in qs:
        uid = item.get('user_id')
        iin = item.get('iin') or ""
        if uid is None:
            # если нет user_id — можно включать записи с iin только (но для select нам нужны id)
            continue
        if uid in seen:
            continue
        seen.add(uid)
        out.append({"user_id": uid, "iin": iin, "first_name": None, "last_name": None})
        user_ids.append(uid)

    # подтянем имена из таблицы auth.User (если есть)
    try:
        users = User.objects.filter(id__in=user_ids).in_bulk()
        for entry in out:
            u = users.get(entry['user_id'])
            if u:
                entry['first_name'] = u.first_name or None
                entry['last_name'] = u.last_name or None
    except Exception:
        pass

    return Response(out)