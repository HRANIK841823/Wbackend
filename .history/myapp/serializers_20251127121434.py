from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Product

User = get_user_model()

# --- User Serializers ---

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'phone_number', 'avatar')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'phone_number', 'balance', 'avatar')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

# --- Product Serializer ---

class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.ReadOnlyField(source='seller.username')
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('seller', 'buyer', 'status', 'created_at')