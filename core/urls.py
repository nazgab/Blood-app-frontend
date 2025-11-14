from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import legacy_views as lviews
from .views import AboutSectionView
from .views_mobile import mobile_home

urlpatterns = [
    # 🩺 Health check
    path("health/", views.health, name="health"),
    # 🌐 Основные публичные API для сайта
    path("site/config/", views.SiteConfigView.as_view(), name="site-config"),
    path("site/menu/", views.MenuListView.as_view(), name="menu-list"),
    path("site/hero/", views.HeroView.as_view(), name="hero"),
    path("articles/", views.ArticleListView.as_view(), name="article-list"),
    path(
        "articles/<slug:slug>/",
        views.ArticleDetailView.as_view(),
        name="article-detail",
    ),
    path("centers/", views.BloodCenterListView.as_view(), name="center-list"),
    path("contacts/", views.ContactListView.as_view(), name="contact-list"),
    path("bonuses/me/", views.BonusMeView.as_view(), name="bonus-me"),
    # 🔐 Аутентификация (через Django пользователей)
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/login/", views.LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    # 🩸 Legacy API — старые таблицы доноров (из PostgreSQL donor_db)
    path("legacy/users/", lviews.LegacyUserListView.as_view(), name="legacy-users"),
    path(
        "legacy/users/<int:user_id>/",
        lviews.LegacyUserDetailView.as_view(),
        name="legacy-user-detail",
    ),
    path("legacy/centers/", lviews.CenterListView.as_view(), name="legacy-centers"),
    path(
        "legacy/users/<int:user_id>/donations/",
        lviews.DonationListByUserView.as_view(),
        name="legacy-user-donations",
    ),
    path(
        "legacy/users/<int:user_id>/bonus/",
        lviews.BonusByUserView.as_view(),
        name="legacy-user-bonus",
    ),
    path("about/", AboutSectionView.as_view(), name="about-section"),
    path("m/", mobile_home, name="mobile_home"),
]
