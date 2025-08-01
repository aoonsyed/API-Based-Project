from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserSignupViewSet, ForgotPasswordView, ResetPasswordView

router = DefaultRouter()
router.register(r"login", AuthViewSet, basename="auth-login")
router.register(r"signup", UserSignupViewSet, basename="user-signup")

urlpatterns = [
    *router.urls,
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
