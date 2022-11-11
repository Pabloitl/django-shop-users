from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from users.models import User
from users.permissions_utils import ActionBasedPermission
from users.serializers import (
    CredentialSerializer,
    PermissionSerializer,
    SafeUserSerializer,
    UserSerializer,
)
from django.contrib.auth.hashers import check_password


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request) -> JsonResponse:
    user = request.user

    return Response(UserSerializer(User.objects.get(id=user.id)).data)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        AllowAny: ["create"],
        IsAdminUser: ["destroy"],
        IsAuthenticated: ["list", "retrieve", "update", "partial_update"],
    }

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer_class = (
            UserSerializer
            if request.data.get("password")
            else SafeUserSerializer
        )
        serializer = serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly createinvalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.save()

        if isinstance(serializer, UserSerializer):
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
