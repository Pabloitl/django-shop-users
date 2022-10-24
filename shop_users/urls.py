from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api/auth/", include("users.urls")),
]
