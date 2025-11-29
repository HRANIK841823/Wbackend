from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "username", "email", "phone_number", "avatar", "balance"]



class ProductSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "user",
            "name",
            "title",
            "description",
            "status",
            "price",
            "location",
            "category",
            "image",  # <--- url string
            "created_at",
        ]


from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    phoneNumber = serializers.CharField(write_only=True)
    avatar = serializers.CharField(required=False, allow_blank=True)  # <--- URL

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phoneNumber', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone = validated_data.pop('phoneNumber')
        avatar_url = validated_data.pop('avatar', None)
        password = validated_data.pop('password')

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(password)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone_number = phone
        if avatar_url:
            profile.avatar = avatar_url
        profile.save()

        return user



class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'product', 'buyer', 'created_at']
