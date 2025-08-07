from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    UserViewSet,
    ContributorViewSet,
    InviteViewSet,
    ContestPerformanceViewSet,
    BadgeViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')  # includes register, login, password-reset, toggle-admin
router.register(r'contributors', ContributorViewSet, basename='contributors')  # contributor register
router.register(r'invites', InviteViewSet, basename='invites')
router.register(r'contest-performance', ContestPerformanceViewSet, basename='contest-performance')
router.register(r'badges', BadgeViewSet, basename='badges')

urlpatterns = [
    path('', include(router.urls)),
]