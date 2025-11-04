# core/views_profile.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm
from .legacy_models import LegacyUser
from .models import Profile

@login_required
def profile_view(request):
    email = (request.user.email or request.user.username).strip()

    # 1) Legacy-пользователь — только просмотр
    legacy = LegacyUser.objects.filter(email__iexact=email).first()
    if legacy:
        return render(request, "profile.html", {
            "mode": "legacy",
            "legacy": legacy,
            "form": None,
        })

    # 2) Новый пользователь — редактирование Profile
    # ГАРАНТИРУЕМ, что у нас есть instance, привязанный к user
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # на всякий случай, если кто-то уберёт instance:
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "profile.html", {
        "mode": "profile",
        "legacy": None,
        "form": form,
    })
