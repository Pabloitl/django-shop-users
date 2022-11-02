from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token

from users.models import User
from users.permissions_utils import ActionBasedPermission
from users.serializers import (
    CredentialSerializer,
    PermissionSerializer,
    UserSerializer,
)
from django.contrib.auth.hashers import check_password
from django.core import serializers


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request) -> JsonResponse:
    return JsonResponse(
        data={
            "id": request.user.id,
        },
        status=HTTP_200_OK,
    )


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAdminUser: ["destroy"],
        IsAuthenticated: ["list", "retrieve", "update", "partial_update", "create"],
    }

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def has_permission(request: HttpRequest):
    serializer = PermissionSerializer(data=request.data)

    if not serializer.is_valid():
        return JsonResponse(
            data={
                "error": "Invalid request",
            },
            status=HTTP_400_BAD_REQUEST,
        )

    permission = serializer.validated_data.pop("permission_name")
    has_permission = False

    if permission == "user":
        has_permission = True

    if permission == "superuser":
        has_permission = request.user.is_superuser

    return JsonResponse(
        data={
            "has_permission": has_permission,
        },
        status=HTTP_200_OK,
    )


@api_view(["POST"])
def login(request: HttpRequest) -> JsonResponse:
    serializer = CredentialSerializer(data=request.data)

    if not serializer.is_valid():
        return JsonResponse(
            data={
                "error": "Invalid request",
            },
            status=HTTP_400_BAD_REQUEST,
        )

    email = serializer.validated_data.pop("email")
    password = serializer.validated_data.pop("password")
    user = User.objects.filter(email=email).first()

    if not user or not check_password(password, user.password):
        return JsonResponse(
            data={
                "error": "Email or password are incorrect",
            },
            status=HTTP_400_BAD_REQUEST,
        )

    return JsonResponse(
        data={
            "token": Token.objects.get_or_create(user=user)[0].key,
        },
        status=HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def logout(request: HttpRequest):
    try:
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist):
        return JsonResponse(
            data={
                "error": "Unable to retrieve token to disable",
            },
            status=HTTP_400_BAD_REQUEST,
        )

    return JsonResponse(
        data={
            "success": True,
        },
        status=HTTP_200_OK,
    )
