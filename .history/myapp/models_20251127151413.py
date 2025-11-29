from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

# 1. Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    def get_by_natural_key(self, email):
        """Required for certain Django behaviors with custom user models."""
        return self.get(**{self.model.USERNAME_FIELD: email}) # Use the email field

# 2. Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255,null=True)
    # 💡 ADD default='0000000000'
    phone_number = models.CharField(max_length=20, default='0000000000') 
    balance = models.FloatField(default=1000.0)
    avatar = models.CharField(max_length=500, blank=True, null=True) # Imgbb Link
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    @property
    def pk(self):
        """Exposes the internal primary key as 'pk' for DRF and Django internals."""
        return self.id

    def __str__(self):
        return self.email

# # 3. Product Model
# import uuid
# from mongoengine import Document, StringField, ReferenceField, DecimalField
# class Product(Document):
#     meta = {'collection': 'products'}
#     id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
#     WASTE_STATUS = (
#         ('available', 'Available'),
#         ('sold', 'Sold'),
#     )
#     CATEGORY_CHOICES = (
#         ('Furniture', 'Furniture'),
#         ('Electronics', 'Electronics'),
#         ('Clothing', 'Clothing'),
#         ('Books', 'Books'),
#         ('Home Decor', 'Home Decor'),
#         ('Toys', 'Toys'),
#         ('Appliances', 'Appliances'),
#         ('Other', 'Other'),
#     )

#     # Seller is the user who posted it
#     seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products_for_sale')
#     # Buyer is added only when status becomes 'sold'
#     buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_products')
    
#     name = models.CharField(max_length=255)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     status = models.CharField(max_length=50, choices=WASTE_STATUS, default='available')
#     price = models.FloatField()
#     location = models.CharField(max_length=255)
#     category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
#     image = models.CharField(max_length=500) # Imgbb direct link
   

#     def __str__(self):
#         return self.title

import uuid
from mongoengine import Document, StringField, ReferenceField, DecimalField, ListField
from django.contrib.auth import get_user_model
from django.db import models # Keep this for CustomUser, but don't use it in Product!

# Get the User model to use in ReferenceField
User = get_user_model() 

class Product(Document):
    meta = {'collection': 'products'}
    
    # 🎯 PRIMARY KEY: MongoEngine StringField mapped to MongoDB '_id'
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # --- Choices (Defined as MongoEngine tuples/lists) ---
    WASTE_STATUS = (
        ('available', 'Available'),
        ('sold', 'Sold'),
    )
    # MongoEngine choice lists are usually simpler strings
    CATEGORY_CHOICES = [
        'Furniture', 'Electronics', 'Clothing', 'Books', 
        'Home Decor', 'Toys', 'Appliances', 'Other',
    ]

    # 🎯 FIX 1: Use ReferenceField for relationships to the User model 🎯
    # Seller is the user who posted it. reverse_delete_rule=2 is MongoEngine's CASCADE
    seller = ReferenceField(User, required=True, reverse_delete_rule=2) 
    # Buyer is optional. null=True is not necessary in MongoEngine but ReferenceField handles it.
    buyer = ReferenceField(User, required=False)
    
    # 🎯 FIX 2: Use StringField/DecimalField for all other fields 🎯
    name = StringField(max_length=255, required=True)
    title = StringField(max_length=255, required=True)
    description = StringField() # MongoEngine equivalent of TextField
    
    # Status and Category fields
    status = StringField(max_length=50, choices=WASTE_STATUS, default='available')
    category = StringField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    
    # Price should be DecimalField for financial accuracy
    price = DecimalField(required=True) 
    location = StringField(max_length=255)
    image = StringField(max_length=500) # Imgbb direct link
    
    # Optional: Keep track of creation time (using datetime or StringField)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title