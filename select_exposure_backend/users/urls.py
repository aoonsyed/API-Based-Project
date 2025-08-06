from django.urls import path
from .views import (
    RegisterView,
    ContributorRegisterView,
    LoginView,
    ToggleAdminStatusView,
    PasswordResetRequestView,
    PasswordResetView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register-contributor/', ContributorRegisterView.as_view(), name='register-contributor'),
    path('login/', LoginView.as_view(), name='login'),
    path('toggle-admin/', ToggleAdminStatusView.as_view(), name='toggle-admin'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
]
