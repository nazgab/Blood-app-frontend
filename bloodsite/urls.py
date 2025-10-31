# bloodsite/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static

# ✅ добавь импорт mobile_home
from core.views_mobile import mobile_home

urlpatterns = [
    path("", RedirectView.as_view(url="/home/", permanent=False)),
    path("home/", TemplateView.as_view(template_name="home.html"), name="home"),

    # ✅ мобильная главная по корню /m/
    path("m/", mobile_home, name="mobile_home"),

    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # API остаётся под /api/v1/
    path("api/v1/", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
