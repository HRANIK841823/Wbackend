from django.db import models
from django.contrib.auth.models import User

WASTE_STATUS = (
    ('available', 'Available'),
    ('pending', 'Pending'),
    ('sold', 'Sold'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20)
    balance = models.FloatField(default=1000.0)  # NEW FIELD
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

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
    ('Other', 'Other'),  # fallback option
)
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=WASTE_STATUS)
    price = models.FloatField()
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')  # NEW
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} bought by {self.buyer.username}"


# 🔔 Signals to auto create UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

import os
from django.db.models.signals import post_save, post_delete, pre_save
# ===========================
#    DELETE IMAGE FILES
# ===========================

# ---- Delete Product Image on Product Delete ----
@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

# ---- Remove old Product image on update ----
@receiver(pre_save, sender=Product)
def update_product_image(sender, instance, **kwargs):
    if not instance.pk:  # new product
        return
    try:
        old_image = Product.objects.get(pk=instance.pk).image
    except Product.DoesNotExist:
        return
    new_image = instance.image
    if old_image != new_image and old_image and os.path.isfile(old_image.path):
        os.remove(old_image.path)

# ---- Delete User Avatar on delete ----
@receiver(post_delete, sender=UserProfile)
def delete_user_avatar(sender, instance, **kwargs):
    if instance.avatar and os.path.isfile(instance.avatar.path):
        os.remove(instance.avatar.path)

# ---- Remove old Avatar on update ----
@receiver(pre_save, sender=UserProfile)
def update_user_avatar(sender, instance, **kwargs):
    if not instance.pk:  # new profile
        return
    try:
        old_avatar = UserProfile.objects.get(pk=instance.pk).avatar
    except UserProfile.DoesNotExist:
        return
    new_avatar = instance.avatar
    if old_avatar != new_avatar and old_avatar and os.path.isfile(old_avatar.path):
        os.remove(old_avatar.path)