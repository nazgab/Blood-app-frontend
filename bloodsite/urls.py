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

urlpatterns = [
    path("", index, name="index"),  # ← корневая, публичная
    path("home/", login_required(TemplateView.as_view(template_name="home.html")), name="home"),
    path("m/", mobile_home, name="mobile_home"),

    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("core.urls")),
    path("accounts/signup/", signup, name="signup"),
    path("accounts/logout/", logout_then_redirect, name="logout"), 
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", profile_view, name="profile"),
    path("medic/donations/", medic_donations, name="medic-donations"),
    path("medic/users/", medic_users, name="medic-users"), 
    path("history/", history, name="history"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
