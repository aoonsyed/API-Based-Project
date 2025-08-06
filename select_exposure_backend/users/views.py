from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, serializers
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import PasswordResetRequestSerializer, PasswordResetSerializer

from .models import User
from .serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    ContributorRegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
)

class ToggleAdminSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_admin = serializers.BooleanField()

class RegisterView(APIView):
    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
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

class ToggleAdminStatusView(APIView):
    @swagger_auto_schema(request_body=ToggleAdminSerializer)
    def post(self, request):
        serializer = ToggleAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        is_admin = serializer.validated_data['is_admin']
        try:
            user = User.objects.get(email__iexact=email)
            user.is_admin = is_admin
            user.save()
            return Response({"message": f"User '{email}' admin status updated to {is_admin}."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

class ContributorRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ContributorRegisterSerializer



# Step 1: Request password reset
class PasswordResetRequestView(APIView):
    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate token with user_id + 'purpose':'reset'
                token = AccessToken.for_user(user)
                token['purpose'] = 'reset'
                # In real app: send email; here, just return the token
                return Response({"reset_token": str(token)}, status=200)
            except User.DoesNotExist:
                return Response({"detail": "User with this email does not exist."}, status=404)
        return Response(serializer.errors, status=400)

class PasswordResetView(APIView):
    @swagger_auto_schema(request_body=PasswordResetSerializer)
    def post(self, request):
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
            except Exception as e:
                return Response({"detail": "Invalid or expired token."}, status=400)
        return Response(serializer.errors, status=400)