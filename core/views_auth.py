# core/views_auth.py
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import SignupForm
from django.contrib.auth import logout


def signup(request):
    # Если уже залогинен — мягко перекидываем в кабинет
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower().strip()
            password = form.cleaned_data["password1"]

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            # автологин
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("home")
    else:
        form = SignupForm()

    return render(request, "registration/signup.html", {"form": form})

def logout_then_redirect(request):
    logout(request)  # очистит сессию
    next_url = request.GET.get("next") or "/"
    return redirect(next_url)