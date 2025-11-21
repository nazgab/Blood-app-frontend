# core/views_auth.py
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import SignupForm
from django.contrib.auth import logout as django_logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy

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

@never_cache
def logout_then_redirect(request):
    """
    Корректный выход: очищаем сессию и редиректим на публичную страницу.
    never_cache -> подсказывает браузеру/прокси не кэшировать ответ.
    При наличии параметра ?next=... — редиректим туда, иначе на 'index'.
    """
    django_logout(request)  # очистит сессию и cookies сессии
    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("index")

class CustomLoginView(DjangoLoginView):
    def get_success_url(self):
        user = self.request.user
        role = getattr(getattr(user, "profile", None), "role", "user")
        if role == "medic":
            return reverse_lazy("medic-home")
        return reverse_lazy("home")