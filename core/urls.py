from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),      # homepage at /
    path('employer/', views.employer, name='employer'),  # employer landing page
    path('signin/', views.signin_register, name='signin_register'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('help-center/', views.help_center, name='help_center'),
    path('accounts/data-deletion/', views.facebook_data_deletion, name='facebook_data_deletion'),
]
