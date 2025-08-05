from rest_framework import serializers
from .models import User, ContributorProfile
from django.contrib.auth.hashers import make_password

# 1. User Registration (for normal user only)
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'screen_name', 'role', 'password', 'confirm_password', 'card_details'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if attrs.get('role', 'user') != 'user':
            raise serializers.ValidationError("For contributors, use the contributor registration endpoint.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        raw_password = validated_data.pop('password')
        validated_data['password'] = make_password(raw_password)
        return User.objects.create(**validated_data)

# 2. Contributor Profile serializer (nested for contributor registration)
class ContributorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContributorProfile
        exclude = ['user']

# 3. Contributor Registration (User + ContributorProfile together)
class ContributorRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    contributor_profile = ContributorProfileSerializer()

    class Meta:
        model = User
        fields = [
            'email', 'screen_name', 'role', 'password', 'confirm_password', 'card_details', 'contributor_profile'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if attrs.get('role', 'contributor') != 'contributor':
            raise serializers.ValidationError("For users, use the user registration endpoint.")
        # ContributorProfile validation will happen through the nested serializer
        return attrs

    def create(self, validated_data):
        contributor_data = validated_data.pop('contributor_profile')
        validated_data.pop('confirm_password')
        raw_password = validated_data.pop('password')
        validated_data['password'] = make_password(raw_password)
        user = User.objects.create(**validated_data)
        ContributorProfile.objects.create(user=user, **contributor_data)
        return user

# 4. Simple login serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

# 5. ToggleAdmin serializer
class ToggleAdminSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_admin = serializers.BooleanField()
