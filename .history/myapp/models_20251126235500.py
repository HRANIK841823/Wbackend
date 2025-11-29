# myapp/models.py
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name='', last_name='', **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name='', last_name='', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        return self.create_user(email, password, first_name, last_name, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # ADD THIS
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)
    avatar = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


#Waste item models 
# myapp/models.py

from django.conf import settings
from bson import ObjectId
class Item(models.Model):
    _id = models.CharField(max_length=100, primary_key=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=255)
    description = models.TextField()

    # category from frontend (string)
    category = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255)

    # available / sold
    status = models.CharField(max_length=20, default="available")

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class PurchaseHistory(models.Model):
    _id = models.CharField(primary_key=True, max_length=100)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales")
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.buyer} bought {self.item}"
