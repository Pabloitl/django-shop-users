from django.contrib.auth.models import (
    AbstractBaseUser,
    AbstractUser,
    PermissionsMixin,
    UnicodeUsernameValidator,
    UserManager,
)
from django.db import models

from shop_users.jwt_utils import generate_jti


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    email = models.EmailField("email address", blank=True, unique=True)

    first_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=10)

    address_line_1 = models.CharField(max_length=150, blank=True)
    address_line_2 = models.CharField(max_length=150, blank=True)
    address_city = models.CharField(max_length=150, blank=True)
    address_state = models.CharField(max_length=150, blank=True)
    address_country = models.CharField(max_length=150, blank=True)
    address_cp = models.IntegerField(blank=True)

    jwt_id = models.CharField(
        max_length=64,
        blank=False,
        null=False,
        editable=False,
        default=generate_jti,
        help_text="JWT tokens for the user get revoked when JWT id has regenerated",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_staff = models.BooleanField(
        default=False,
    )
