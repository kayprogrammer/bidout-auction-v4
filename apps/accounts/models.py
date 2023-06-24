import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel, File
from datetime import datetime
from django.conf import settings
from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(verbose_name=(_("Email address")), unique=True)
    avatar = models.ForeignKey(
        File, to_field="id", on_delete=models.SET_NULL, null=True
    )

    terms_agreement = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Jwt(BaseModel):
    user = models.OneToOneField(User, to_field="id", on_delete=models.CASCADE)
    access = models.TextField()
    refresh = models.TextField()


class Otp(BaseModel):
    user = models.OneToOneField(User, to_field="id", on_delete=models.CASCADE)
    access = models.TextField()
    refresh = models.TextField()

    def check_expiration(self):
        now = datetime.utcnow()
        diff = now - self.updated_at
        if diff.total_seconds() > settings.EMAIL_OTP_EXPIRE_SECONDS:
            return True
        return False
