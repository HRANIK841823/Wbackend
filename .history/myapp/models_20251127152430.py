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

# 3. Product Model

from mongoengine import Document, StringField, ReferenceField, DecimalField, SequenceField # Keep these
# Remove: from django.db import models (since this is only for CustomUser now)
# We must include the primary key field for MongoEngine (using the default ObjectId structure)

# Get the User model to use in ReferenceField


class Product(Document):
    meta = {'collection': 'products'}

    # 🎯 FIX 1: The actual primary key is MongoDB's _id. We don't define 'id' or '_id' here
    # and let MongoEngine handle the default ObjectId primary key.
    
    # 🎯 FIX 2: Correctly define the sequence field 
    product_number = SequenceField(unique=True) 

    WASTE_STATUS = (
        ('available', 'Available'),
        ('sold', 'Sold'),
    )
    CATEGORY_CHOICES = [
        'Furniture', 'Electronics', 'Clothing', 'Books', 'Home Decor', 
        'Toys', 'Appliances', 'Other',
    ]

    # 🎯 FIX 3: Replace models.ForeignKey with ReferenceField 🎯
    seller = ReferenceField('myapp.CustomUser', required=True) 
    buyer = ReferenceField('myapp.CustomUser', required=False)
    
    # 🎯 FIX 4: Replace models.CharField/TextField/FloatField with StringField/DecimalField 🎯
    name = StringField(max_length=255, required=True)
    title = StringField(max_length=255, required=True)
    description = StringField() # MongoEngine equivalent of TextField
    status = StringField(max_length=50, choices=WASTE_STATUS, default='available')
    price = DecimalField(required=True) 
    location = StringField(max_length=255)
    category = StringField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    image = StringField(max_length=500)
    
    # We'll need a created_at field for history
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title