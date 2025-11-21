from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")
    id = serializers.IntegerField(source="user.id", read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "username", "email", "phone_number", "avatar", "balance"]

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else None


class ProductSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.SerializerMethodField()

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
            "image",
            "created_at",
        ]

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class RegisterSerializer(serializers.ModelSerializer):
    phoneNumber = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phoneNumber', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone = validated_data.pop('phoneNumber')
        avatar = validated_data.pop('avatar', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        profile = user.profile
        profile.phone_number = phone
        if avatar:
            profile.avatar = avatar
        profile.save()

        return user


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'product', 'buyer', 'created_at']
