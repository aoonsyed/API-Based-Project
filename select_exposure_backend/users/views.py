from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .serializers import UserRegisterSerializer, LoginSerializer
from .models import User
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from .models import User
from .serializers import ContributorRegisterSerializer


# ------- ToggleAdminSerializer ---------
class ToggleAdminSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_admin = serializers.BooleanField()

# ------- RegisterView ---------
class RegisterView(APIView):
    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Registration successful."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ------- LoginView ---------
class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(email=email)
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

# ------- ToggleAdminStatusView ---------
class ToggleAdminStatusView(APIView):
    @swagger_auto_schema(request_body=ToggleAdminSerializer)
    def post(self, request):
        serializer = ToggleAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        is_admin = serializer.validated_data['is_admin']
        try:
            user = User.objects.get(email=email)
            user.is_admin = is_admin
            user.save()
            return Response({
                "message": f"User '{email}' admin status updated to {is_admin}."
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

class ContributorRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = ContributorRegisterSerializer