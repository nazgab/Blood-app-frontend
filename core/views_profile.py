from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm
from .legacy_models import LegacyUser
from .models import Profile, Employee
from django.views.decorators.cache import never_cache

@login_required
@never_cache
def profile_view(request):
    # email для поиска legacy
    email = (request.user.email or request.user.username or "").strip()

    # 1) legacy — только просмотр
    legacy = LegacyUser.objects.filter(email__iexact=email).first()
    if legacy:
        return render(request, "profile.html", {
            "mode": "legacy",
            "legacy": legacy,
            "form": None,
            "profile": None,
            "employee": None,
        })

    # 2) профиль пользователя
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # сначала найдём employee (по id, затем по имени/фамилии — fallback)
    employee = None
    if getattr(profile, "employee_id", None):
        employee = Employee.objects.filter(employee_id=profile.employee_id).first()

    if not employee:
        fn = (profile.first_name or "").strip()
        ln = (profile.last_name or "").strip()
        if fn and ln:
            employee = Employee.objects.filter(first_name__iexact=fn, last_name__iexact=ln).first()

    # форма для редактирования (всегда создаём, но рендер решит что показывать)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    # --- Подготовим безопасные переменные для шаблона ---
    # middle_display: то, что показываем в поле "Отчество" (или где хотим показать должность)
    # логика: если есть employee.position — используем её, иначе берём profile.middle / profile.middle_name (если есть)
    middle_display = None
    if employee and getattr(employee, "position", None):
        middle_display = employee.position
    else:
        # безопасно пытаемся взять возможные поля в profile
        middle_display = getattr(profile, "middle", None) or getattr(profile, "middle_name", None)

    # телефон и email для удобного вывода в шаблоне
    display_phone = (employee.phone if employee and getattr(employee, "phone", None) else profile.phone or "")
    display_email = request.user.email or ""

    # флаг — является ли пользователь медиком (чтобы шаблон мог спрятать вес/группу крови и т.д.)
    is_medic = (profile and ( (profile.role or "").lower() == "medic" ))

    return render(request, "profile.html", {
        "mode": "profile",
        "legacy": None,
        "form": form,
        "profile": profile,
        "employee": employee,
        # дополнительные контекстные переменные:
        "middle_display": middle_display,
        "display_phone": display_phone,
        "display_email": display_email,
        "is_medic": is_medic,
    })
