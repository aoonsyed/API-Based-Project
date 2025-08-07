from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import (
    UserViewSet,
    ContributorViewSet,
    InviteViewSet,
    ContestPerformanceViewSet,
    BadgeViewSet, ContestViewSet, ContestEntryViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'contributors', ContributorViewSet, basename='contributors')
router.register(r'invites', InviteViewSet, basename='invites')
router.register(r'contest-performance', ContestPerformanceViewSet, basename='contest-performance')
router.register(r'badges', BadgeViewSet, basename='badges')
router.register(r'contests', ContestViewSet, basename='contests')
router.register(r'contests_entry', ContestEntryViewSet, basename='contests-entry')

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Select Exposure API",
        default_version='v1',
        description="API documentation for Select Exposure platform",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]