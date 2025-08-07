from datetime import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import get_user_model

from .models import User, Invite, ContestPerformance, Badge
from .serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    ContributorRegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    ToggleAdminSerializer,
    InviteSerializer,
    ContestPerformanceSerializer,
    BadgeSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer 

    @swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='post', request_body=LoginSerializer)
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip().lower()
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, user.password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.id,
                "role": user.role,
            })
        else:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(method='post', request_body=ToggleAdminSerializer)
    @action(detail=False, methods=['post'], url_path='toggle-admin')
    def toggle_admin(self, request):
        serializer = ToggleAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        is_admin = serializer.validated_data['is_admin']
        try:
            user = User.objects.get(email__iexact=email)
            user.is_admin = is_admin
            user.save()
            return Response({"message": f"User '{email}' admin status updated to {is_admin}."},
                            status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(method='post', request_body=PasswordResetRequestSerializer)
    @action(detail=False, methods=['post'], url_path='password-reset-request')
    def password_reset_request(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = AccessToken.for_user(user)
                token['purpose'] = 'reset'
                return Response({"reset_token": str(token)}, status=200)
            except User.DoesNotExist:
                return Response({"detail": "User with this email does not exist."}, status=404)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(method='post', request_body=PasswordResetSerializer)
    @action(detail=False, methods=['post'], url_path='password-reset')
    def password_reset(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            confirm_password = serializer.validated_data['confirm_password']
            if new_password != confirm_password:
                return Response({"detail": "Passwords do not match."}, status=400)
            try:
                decoded = AccessToken(token)
                if decoded.get('purpose') != 'reset':
                    return Response({"detail": "Invalid token."}, status=400)
                user_id = decoded['user_id']
                user = User.objects.get(id=user_id)
                user.password = make_password(new_password)
                user.save()
                return Response({"message": "Password reset successful."}, status=200)
            except Exception:
                return Response({"detail": "Invalid or expired token."}, status=400)
        return Response(serializer.errors, status=400)


class ContributorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = ContributorRegisterSerializer


class InviteViewSet(viewsets.ModelViewSet):
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Invite.objects.none()
        return Invite.objects.filter(sender=self.request.user).order_by('-sent_at')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user, sent_at=timezone.now())


class ContestPerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = ContestPerformanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ContestPerformance.objects.none()
        return ContestPerformance.objects.filter(user=self.request.user).order_by('-win_date')


class BadgeViewSet(viewsets.ModelViewSet):
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Badge.objects.none()
        return Badge.objects.filter(user=self.request.user)
