from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, has_permission, login, logout, me

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("me/", me),
    path("login/", login),
    path("logout/", logout),
    path("can/", has_permission),
    path("", include(router.urls)),
]
