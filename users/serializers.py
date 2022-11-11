from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from users.models import User


class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        exclude = [
            "is_staff",
            "jwt_id",
            "groups",
            "user_permissions",
            "last_login",
        ]


class SafeUserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = [
            "is_staff",
            "jwt_id",
            "groups",
            "user_permissions",
            "last_login",
            "password",
        ]


class CredentialSerializer(Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class PermissionSerializer(Serializer):
    permission_name = serializers.CharField()
