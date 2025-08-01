from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.utils.crypto import get_random_string

from .models import User
from .serializers import (
    UserSignupSerializer,
    UserLoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)

# In-memory dict for demo (use DB or cache in production!)
RESET_TOKENS = {}

class AuthViewSet(viewsets.ViewSet):
    @extend_schema(
        summary="Login with email and password to receive JWT tokens.",
        description="Login API. Returns JWT tokens on valid credentials.",
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(description="Token retrieved successfully"),
            400: OpenApiResponse(description="Invalid credentials"),
        },
    )
    def create(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        user = User.objects.filter(email=email).first()
        if user and check_password(password, user.password):
            token = RefreshToken.for_user(user)
            data = {
                "refresh_token": str(token),
                "access_token": str(token.access_token),
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "isadmin": user.isadmin,
            }
            return Response(
                {"message": "Logged in successfully", "data": data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Invalid email or password.", "data": {}},
                status=status.HTTP_400_BAD_REQUEST,
            )

class UserSignupViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    http_method_names = ["post"]

    @extend_schema(
        summary="Signup a new user.",
        description="Signup API. Creates a new user.",
        request=UserSignupSerializer,
        responses={
            201: OpenApiResponse(description="User created successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "User created successfully.", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        return serializer.save()

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Request password reset email.",
        description="Send a password reset link to email if it exists.",
        request=ForgotPasswordSerializer,
        responses={200: OpenApiResponse(description="Reset link sent")},
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            # Create a reset token (use JWT or UUID in production)
            token = get_random_string(32)
            RESET_TOKENS[token] = user.id
            # Here you would send an email! (Just print for now)
            print(f"[DEBUG] Reset link: http://localhost:8000/api/accounts/reset-password/?token={token}")
        return Response({"message": "If your email exists, a reset link has been sent."})

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Reset password with token.",
        description="Reset password via link sent to email.",
        request=ResetPasswordSerializer,
        responses={200: OpenApiResponse(description="Password reset")},
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        user_id = RESET_TOKENS.get(token)
        if not user_id:
            return Response({"message": "Invalid or expired token."}, status=400)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"message": "User not found."}, status=404)
        user.password = make_password(password)
        user.save()
        # Remove used token
        del RESET_TOKENS[token]
        return Response({"message": "Password reset successfully."})
