from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from core.views_mobile import mobile_home
from core.views_public import index  # ← добавили
from core.views_auth import signup, logout_then_redirect 
from core.views_profile import profile_view
from core.views_auth import CustomLoginView 
from core.views_medic import medic_donations
from core.views_medic import medic_users
from core.views_pages import history
from django.contrib.auth import views as auth_views
from core.views import donate_view

urlpatterns = [
    path("", index, name="index"),  # ← корневая, публичная
    path("home/", login_required(TemplateView.as_view(template_name="home.html")), name="home"),
    path("bonuses/", login_required(TemplateView.as_view(template_name="bonuses.html")), name="bonuses"),
    path("m/", mobile_home, name="mobile_home"),

    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("core.urls")),
    path("accounts/signup/", signup, name="signup"),
    path("accounts/logout/", logout_then_redirect, name="logout"), 
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", profile_view, name="profile"),
    path("medic/donations/", medic_donations, name="medic-donations"),
    path("medic/users/", medic_users, name="medic-users"), 
    path("history/", history, name="history"),
    path("donate/", donate_view, name="donate"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
