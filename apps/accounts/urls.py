from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
