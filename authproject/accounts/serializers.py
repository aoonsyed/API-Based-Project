from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class UserSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user signup
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'isadmin', 'password', 'role']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password (send email)
    """
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting password
    """
    token = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)
