from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from core import views as core_views
from accounts import views as account_views

urlpatterns = [
    # --- DJANGO ADMIN ---
    path("admin/", admin.site.urls),
    path('accounts/', include('accounts.urls')),

    # --- MAIN PAGES ---
    path("", core_views.homepage, name="homepage"),
    path("homepage/", core_views.homepage),
    path("about/", TemplateView.as_view(template_name="core/about.html"), name="about"),

    # --- SOCIAL LOGIN ROLE SELECTION (MUST COME BEFORE ALLAUTH) ---
    path('select-role/', account_views.select_role, name='select_role'),
    path('select-employer-type/', account_views.select_employer_type, name='select_employer_type'),
    path('complete-social-profile/', account_views.complete_social_profile, name='complete_social_profile'),

    # --- APP ROUTES ---
    path("", include("core.urls")),
    path("jobs/", include("jobs.urls")),
    path("system-admin/", include("accounts.urls")),

    # --- AUTHENTICATION (YOUR CUSTOM PAGES) ---
    path("signin_register/", account_views.signin_register, name="signin_register"),
    path("logout/", account_views.logout_view, name="logout_view"),

    # --- OTP ---
    path("send-otp/", account_views.send_otp, name="send_otp"),
    path("verify-otp/", account_views.verify_otp, name="verify_otp"),

    # --- PASSWORD RESET ---
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(template_name="core/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(template_name="core/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="core/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="core/password_reset_complete.html"),
        name="password_reset_complete",
    ),

    # --- PASSWORD CHANGE ---
    path("password/change/", account_views.password_change, name="password_change"),
    path("password/change/done/", account_views.password_change_done, name="password_change_done"),
    
    # ✅ ACCOUNTS URLS (INCLUDES YOUR CUSTOM VIEWS) - BEFORE ALLAUTH
    path("accounts/", include("accounts.urls")),
    
    # ✅ OAUTH URLS - MUST COME LAST
    path('accounts/', include('allauth.urls')),
]

# --- MEDIA SERVING ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)