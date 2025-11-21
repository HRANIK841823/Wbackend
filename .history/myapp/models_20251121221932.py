# models.py
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

WASTE_STATUS = (
    ('available', 'Available'),
    ('pending', 'Pending'),
    ('sold', 'Sold'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20)
    balance = models.FloatField(default=1000.0)
    avatar = CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return self.user.username


CATEGORY_CHOICES = (
    ('Furniture', 'Furniture'),
    ('Electronics', 'Electronics'),
    ('Clothing', 'Clothing'),
    ('Books', 'Books'),
    ('Home Decor', 'Home Decor'),
    ('Toys', 'Toys'),
    ('Appliances', 'Appliances'),
    ('Other', 'Other'),
)

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=WASTE_STATUS)
    price = models.FloatField()
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    image = CloudinaryField('image', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} bought by {self.buyer.username}"



# signals.py (recommended file)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)





