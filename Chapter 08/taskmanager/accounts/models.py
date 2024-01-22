from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255)


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("organization_id", 1)  # or another default value

        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class TaskManagerUser(AbstractUser):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField()

    objects = CustomUserManager()

    class Meta:
        unique_together = ("organization", "username", "email")
