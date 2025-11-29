# myapp/serializers.py

from rest_framework import serializers
from django.contrib.auth import password_validation
from .models import CustomUser, Item, PurchaseHistory
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# -------------------------------
# Register
# -------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'avatar')

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        password_validation.validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        return CustomUser.objects.create_user(password=password, **validated_data)


# -------------------------------
# User Serializer
# -------------------------------
class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="_id", read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number',
                  'balance', 'avatar', 'date_joined')


# -------------------------------
# Profile Update
# -------------------------------
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'avatar', 'phone_number')


# -------------------------------
# Change Password
# -------------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context['request'].user)
        return value


# -------------------------------
# JWT Token Serializer
# -------------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["id"] = user._id
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        return token


# -------------------------------
# Item Serializers
# -------------------------------
class ItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="_id", read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'category', 'price',
                  'image_url', 'location', 'status', 'seller', 'created_at']


class ItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'price', 'image_url', 'location']


# -------------------------------
# Purchase Serializer
# -------------------------------
class PurchaseSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="_id", read_only=True)
    item_title = serializers.CharField(source='item.title', read_only=True)

    class Meta:
        model = PurchaseHistory
        fields = ['id', 'item_title', 'price', 'created_at', 'buyer', 'seller']
