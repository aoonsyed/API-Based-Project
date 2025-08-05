from django.urls import path
from .views import RegisterView, ContributorRegisterView, LoginView, ToggleAdminStatusView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register-contributor/', ContributorRegisterView.as_view(), name='register-contributor'),
    path('login/', LoginView.as_view(), name='login'),
    path('toggle-admin/', ToggleAdminStatusView.as_view(), name='toggle-admin'),
]
