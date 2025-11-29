# myapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate, password_validation
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        # Ensure phone_number is included here
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password', 'password2', 'avatar')

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({'password': "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        # CustomUser.objects.create_user handles the remaining fields like first_name, last_name, phone_number, etc.
        user = CustomUser.objects.create_user(password=password, **validated_data) 
        return user


class UserSerializer(serializers.ModelSerializer):
    # REMOVED: id = serializers.CharField(source='_id', read_only=True) 
    # This line is part of the _id conflict issue and is addressed in Section 2.

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'balance', 'avatar', 'date_joined')
        read_only_fields = ('id', 'email', 'balance', 'date_joined')

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'avatar', 'phone_number') # phone_number is included
        # Add read_only_fields for clarity, though not strictly needed here
        read_only_fields = ('email', 'balance', 'date_joined')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value, user=self.context['request'].user)
        return value

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token
